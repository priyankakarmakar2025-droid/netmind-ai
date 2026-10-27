import re
import json
import csv
import io
from typing import List, Dict, Any, Tuple
from datetime import datetime

LOG_REGEX_PATTERNS = [
    # Format 1: [YYYY-MM-DD HH:MM:SS] [SEVERITY] [HOST/SERVICE] Message
    re.compile(r"^\[(?P<timestamp>[^\]]+)\]\s+\[(?P<severity>[A-Z]+)\]\s+\[(?P<service>[^\]]+)\]\s+(?P<message>.*)$"),
    # Format 2: Syslog style: Oct 27 10:15:32 hostname daemon[pid]: message
    re.compile(r"^(?P<timestamp>[A-Za-z]{3}\s+\d+\s+\d+:\d+:\d+)\s+(?P<hostname>\S+)\s+(?P<service>[^:\[]+)(?:\[\d+\])?:\s+(?P<message>.*)$"),
    # Format 3: Timestamp IP -> IP Protocol Message
    re.compile(r"^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d+:\d+:\d+)\s+(?P<src_ip>\d+\.\d+\.\d+\.\d+)\s+->\s+(?P<dst_ip>\d+\.\d+\.\d+\.\d+)\s+(?P<protocol>[A-Z]+)\s+(?P<message>.*)$")
]

IP_REGEX = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

class LogParserService:
    @staticmethod
    def parse_content(filename: str, content: str) -> Tuple[List[Dict[str, Any]], int, int, List[str]]:
        events = []
        errors = []
        rejected_count = 0
        parsed_count = 0

        # JSON / JSONL
        if filename.endswith(".json") or filename.endswith(".jsonl"):
            lines = content.strip().split("\n")
            # Try full JSON array first
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    for item in data:
                        parsed_count += 1
                        events.append(LogParserService._normalize_dict(item))
                    return events, parsed_count, rejected_count, errors
            except Exception:
                pass

            # Try Line by Line JSONL
            for line_no, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    events.append(LogParserService._normalize_dict(obj))
                    parsed_count += 1
                except Exception as e:
                    rejected_count += 1
                    errors.append(f"Line {line_no}: Invalid JSON - {str(e)}")
            return events, parsed_count, rejected_count, errors

        # CSV
        if filename.endswith(".csv"):
            f = io.StringIO(content)
            reader = csv.DictReader(f)
            for row_no, row in enumerate(reader, 1):
                try:
                    events.append(LogParserService._normalize_dict(row))
                    parsed_count += 1
                except Exception as e:
                    rejected_count += 1
                    errors.append(f"Row {row_no}: {str(e)}")
            return events, parsed_count, rejected_count, errors

        # Plain text / .log
        for line_no, raw_line in enumerate(content.splitlines(), 1):
            line = raw_line.strip()
            if not line:
                continue
            matched = False
            for pat in LOG_REGEX_PATTERNS:
                m = pat.match(line)
                if m:
                    data = m.groupdict()
                    evt = {
                        "timestamp": LogParserService._parse_time(data.get("timestamp")),
                        "severity": data.get("severity", "INFO").upper(),
                        "service_name": data.get("service"),
                        "hostname": data.get("hostname"),
                        "source_ip": data.get("src_ip"),
                        "dest_ip": data.get("dst_ip"),
                        "protocol": data.get("protocol", "TCP"),
                        "message": data.get("message", line),
                        "event_type": LogParserService._infer_event_type(data.get("message", line)),
                        "raw_line": raw_line
                    }
                    events.append(evt)
                    parsed_count += 1
                    matched = True
                    break
            if not matched:
                # Generic fallback extraction
                ips = IP_REGEX.findall(line)
                events.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "WARNING" if any(w in line.lower() for w in ["warn", "fail", "drop", "err", "down"]) else "INFO",
                    "service_name": "system",
                    "hostname": "gateway",
                    "source_ip": ips[0] if len(ips) > 0 else "127.0.0.1",
                    "dest_ip": ips[1] if len(ips) > 1 else None,
                    "protocol": "TCP",
                    "message": line,
                    "event_type": LogParserService._infer_event_type(line),
                    "raw_line": raw_line
                })
                parsed_count += 1

        return events, parsed_count, rejected_count, errors

    @staticmethod
    def _parse_time(time_str: str) -> str:
        if not time_str:
            return datetime.utcnow().isoformat()
        try:
            return datetime.fromisoformat(time_str).isoformat()
        except Exception:
            return datetime.utcnow().isoformat()

    @staticmethod
    def _normalize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        msg = d.get("message", d.get("msg", str(d)))
        return {
            "timestamp": str(d.get("timestamp", datetime.utcnow().isoformat())),
            "severity": str(d.get("severity", d.get("level", "INFO"))).upper(),
            "service_name": d.get("service_name", d.get("service", "daemon")),
            "hostname": d.get("hostname", d.get("host")),
            "source_ip": d.get("source_ip", d.get("src_ip", "192.168.1.101")),
            "dest_ip": d.get("dest_ip", d.get("dst_ip")),
            "protocol": d.get("protocol", "TCP"),
            "message": msg,
            "event_type": d.get("event_type", LogParserService._infer_event_type(msg)),
            "raw_line": json.dumps(d)
        }

    @staticmethod
    def _infer_event_type(msg: str) -> str:
        m = msg.lower()
        if "dns" in m or "resolve" in m or "nxdomain" in m or "port 53" in m:
            return "DNS_LOOKUP_FAILURE"
        if "dhcp" in m or "lease" in m or "discover" in m or "udp 67" in m:
            return "DHCP_ALLOC_FAILURE"
        if "timeout" in m or "etimedout" in m:
            return "TCP_TIMEOUT"
        if "unreachable" in m or "route" in m or "next hop" in m:
            return "ROUTING_ERROR"
        if "packet loss" in m or "dropped" in m or "retransmit" in m:
            return "PACKET_LOSS"
        if "firewall" in m or "acl" in m or "blocked" in m or "denied" in m:
            return "FIREWALL_DENIAL"
        if "database" in m or "postgres" in m or "connection pool" in m or "deadlock" in m:
            return "DB_DEPENDENCY_FAILURE"
        if "502" in m or "500" in m or "upstream" in m:
            return "WEB_SERVICE_FAILURE"
        return "GENERAL_NETWORK_EVENT"

log_parser = LogParserService()

#!/usr/bin/env python3
import time
import sys
import pymysql
from pymysql.cursors import DictCursor
import requests
from typing import Dict, List

def check_node_status(host: str, port: int) -> Dict[str, str]:
    """Check the status of a single MariaDB node."""
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user='app_user',
            password='app_password',
            database='event_booking',
            cursorclass=DictCursor
        )

        with conn.cursor() as cursor:
            cursor.execute("SHOW STATUS LIKE 'wsrep_%'")
            status = {row['Variable_name']: row['Value'] 
                     for row in cursor.fetchall()}

            return {
                'node': f"{host}:{port}",
                'cluster_size': status.get('wsrep_cluster_size', 'N/A'),
                'cluster_status': status.get('wsrep_cluster_status', 'N/A'),
                'state_comment': status.get('wsrep_local_state_comment', 'N/A'),
                'connected': status.get('wsrep_connected', 'N/A'),
                'ready': status.get('wsrep_ready', 'N/A')
            }
    except Exception as e:
        return {
            'node': f"{host}:{port}",
            'cluster_size': 'N/A',
            'cluster_status': 'ERROR',
            'state_comment': str(e),
            'connected': 'NO',
            'ready': 'NO'
        }

def check_haproxy_status() -> Dict[str, str]:
    """Check HAProxy statistics."""
    try:
        response = requests.get(
            'http://localhost:18404',
            auth=('admin', 'password')
        )
        return {
            'status': 'OK' if response.status_code == 200 else 'ERROR',
            'message': f"Status code: {response.status_code}"
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'message': str(e)
        }

def monitor_cluster(interval: int = 5):
    """Monitor the health of the Galera cluster."""
    nodes = [
        ('localhost', 13306),
        ('localhost', 13307),
        ('localhost', 13308)
    ]

    while True:
        print("\n=== Cluster Health Check ===")
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check each node
        node_statuses = []
        for host, port in nodes:
            status = check_node_status(host, port)
            node_statuses.append(status)
            
            print(f"\nNode: {status['node']}")
            print(f"Cluster Size: {status['cluster_size']}")
            print(f"Cluster Status: {status['cluster_status']}")
            print(f"State: {status['state_comment']}")
            print(f"Connected: {status['connected']}")
            print(f"Ready: {status['ready']}")

        # Check HAProxy
        haproxy = check_haproxy_status()
        print("\nHAProxy Status:")
        print(f"Status: {haproxy['status']}")
        print(f"Message: {haproxy['message']}")

        # Check for issues
        issues = []
        expected_cluster_size = '3'
        
        for status in node_statuses:
            if status['cluster_status'] != 'Primary':
                issues.append(f"Node {status['node']} is not in Primary state")
            if status['cluster_size'] != expected_cluster_size:
                issues.append(f"Node {status['node']} reports wrong cluster size")
            if status['ready'] != 'ON':
                issues.append(f"Node {status['node']} is not ready")

        if haproxy['status'] != 'OK':
            issues.append("HAProxy is not functioning properly")

        if issues:
            print("\nIssues Detected:")
            for issue in issues:
                print(f"- {issue}")
        else:
            print("\nNo issues detected. Cluster is healthy.")

        sys.stdout.flush()
        time.sleep(interval)

if __name__ == '__main__':
    try:
        monitor_cluster()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 
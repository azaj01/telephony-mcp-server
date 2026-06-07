#!/usr/bin/env python3
"""
Test script to verify OpenLIT telemetry is working with the MCP server.
This script initializes OpenLIT and makes a simple HTTP request to generate telemetry data.
"""
import openlit
import httpx
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenLIT with the OTLP endpoint
logger.info("Initializing OpenLIT...")
openlit.init(
    otlp_endpoint="http://127.0.0.1:4318",
    application_name="telephony-mcp-test",
)
logger.info("✓ OpenLIT initialized with endpoint: http://127.0.0.1:4318")

# Make a simple HTTP request to generate telemetry
logger.info("Making test HTTP request to generate telemetry data...")
try:
    with httpx.Client() as client:
        response = client.get("https://httpbin.org/get")
        logger.info(f"✓ Test request completed with status: {response.status_code}")
except Exception as e:
    logger.error(f"✗ Test request failed: {e}")

# Give OpenLIT time to export the telemetry
logger.info("Waiting for telemetry export...")
time.sleep(2)

logger.info("✓ Test completed! Check your OTLP collector for telemetry data.")
logger.info("  Expected application name: telephony-mcp-test")
logger.info("  Expected traces: HTTP GET request to httpbin.org")

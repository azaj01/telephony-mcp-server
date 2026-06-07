#!/usr/bin/env python3
"""
Quick test script for MCP SMS client
Replace the phone number with a real one to test
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_client import send_sms_via_mcp


async def main():
    """
    Test sending an SMS via MCP
    """
    # IMPORTANT: Replace with actual phone numbers for testing
    TO_NUMBER = "+14155551234"  # Replace with destination number
    FROM_NUMBER = None  # Will use server default (VONAGE_LVN)
    MESSAGE = "Test message from MCP client!"
    
    print("=" * 60)
    print("🧪 Testing MCP SMS Client")
    print("=" * 60)
    print(f"\n⚠️  Make sure to update TO_NUMBER in this script!")
    print(f"Current settings:")
    print(f"  To: {TO_NUMBER}")
    print(f"  From: {FROM_NUMBER or 'Server default'}")
    print(f"  Message: {MESSAGE}")
    print("\n" + "=" * 60 + "\n")
    
    response = input("Continue with test? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Test cancelled")
        return
    
    # Send SMS
    await send_sms_via_mcp(
        to_number=TO_NUMBER,
        message=MESSAGE,
        from_number=FROM_NUMBER
    )
    
    print("\n" + "=" * 60)
    print("🎉 Test completed!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("  - Check OpenLIT dashboard: http://localhost:3000")
    print("  - View server logs for detailed trace information")
    print("  - Check Vonage dashboard for SMS delivery status")


if __name__ == "__main__":
    asyncio.run(main())

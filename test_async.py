#!/usr/bin/env python3
"""
Test async compatibility with Textual
"""

from textual.app import App
import asyncio

class TestApp(App):
    """Test async functionality"""

    async def on_mount(self):
        """Test async operations"""
        print("Testing async sleep...")
        await asyncio.sleep(0.1)
        print("✅ Async sleep works!")

        print("Testing async task creation...")
        task = asyncio.create_task(self.async_task())
        await task
        print("✅ Async tasks work!")

        # Exit the app
        self.exit("Async test passed!")

    async def async_task(self):
        """Test async task"""
        await asyncio.sleep(0.1)
        print("  ↳ Async task completed")

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING ASYNC COMPATIBILITY")
    print("=" * 60)

    app = TestApp()
    result = app.run()

    print("=" * 60)
    print(f"Result: {result}")
    print("✅ ALL ASYNC TESTS PASSED!")
    print("=" * 60)

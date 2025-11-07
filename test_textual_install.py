#!/usr/bin/env python3
"""
Test Textual installation by creating a simple app
"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Button
from textual.containers import Container

class TestApp(App):
    """Test app to verify Textual installation"""

    CSS = """
    Screen {
        align: center middle;
    }

    #test-container {
        width: 50;
        height: 15;
        border: solid green;
        background: $surface;
    }

    Static {
        text-align: center;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="test-container"):
            yield Static("🐄 Textual Installation Test 🐄", classes="title")
            yield Static("If you can see this, Textual is working!")
            yield Static(f"Textual version: {self.app.__class__.__module__}")
            yield Button("Exit Test", id="exit", variant="success")

    def on_mount(self) -> None:
        """Auto-exit after 2 seconds for automated testing"""
        self.set_timer(2, self.exit)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        if event.button.id == "exit":
            self.exit()

if __name__ == "__main__":
    app = TestApp()
    result = app.run()
    print("\n✅ Textual installation test PASSED!")
    print(f"   App exited successfully")

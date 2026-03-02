"""
Bronze Tier Verification Test

Run this script to verify all components are working.
"""

from pathlib import Path
import sys

def test_imports():
    """Test 1: Verify all imports work."""
    print("=" * 60)
    print("TEST 1: Python Imports")
    print("=" * 60)
    try:
        from watchers import BaseWatcher, FileSystemWatcher
        print("  [OK] Watchers module imported successfully")
        from orchestrator import Orchestrator
        print("  [OK] Orchestrator module imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        return False

def test_vault_structure():
    """Test 2: Verify vault folder structure."""
    print("\n" + "=" * 60)
    print("TEST 2: Vault Folder Structure")
    print("=" * 60)
    
    vault = Path("AI_Employee_Vault")
    required_folders = [
        "Inbox", "Needs_Action", "Done", "Plans",
        "Pending_Approval", "Approved", "Accounting",
        "Briefings", "Invoices", "Logs", "Drop_Folder"
    ]
    
    all_exist = True
    for folder in required_folders:
        folder_path = vault / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"  [OK] {folder}/")
        else:
            print(f"  [MISSING] {folder}/")
            all_exist = False
    
    return all_exist

def test_vault_files():
    """Test 3: Verify vault markdown files."""
    print("\n" + "=" * 60)
    print("TEST 3: Vault Markdown Files")
    print("=" * 60)
    
    vault = Path("AI_Employee_Vault")
    required_files = [
        "Dashboard.md",
        "Company_Handbook.md",
        "Business_Goals.md"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = vault / file
        if file_path.exists():
            print(f"  [OK] {file}")
        else:
            print(f"  [MISSING] {file}")
            all_exist = False
    
    return all_exist

def test_watcher():
    """Test 4: Test File System Watcher."""
    print("\n" + "=" * 60)
    print("TEST 4: File System Watcher")
    print("=" * 60)
    
    from watchers.filesystem_watcher import FileSystemWatcher
    
    # Clean folders
    vault = Path("AI_Employee_Vault")
    for f in (vault / "Needs_Action").glob("*.md"):
        f.unlink()
    for f in (vault / "Drop_Folder").glob("*"):
        f.unlink()
    print("  [OK] Cleaned test folders")
    
    # Initialize watcher
    watcher = FileSystemWatcher(str(vault))
    print("  [OK] Watcher initialized")
    
    # Create test file
    test_file = vault / "Drop_Folder" / "test_invoice.pdf"
    test_file.write_bytes(b"%PDF-test-invoice")
    print("  [OK] Created test file: test_invoice.pdf")
    
    # Detect file
    items = watcher.check_for_updates()
    if len(items) > 0:
        print(f"  [OK] Detected {len(items)} new file(s)")
    else:
        print("  [FAIL] Failed to detect new file")
        return False
    
    # Create action file
    for item in items:
        action = watcher.create_action_file(item)
        if action:
            print(f"  [OK] Created action file: {action.name}")
        else:
            print("  [FAIL] Failed to create action file")
            return False
    
    # Verify action file exists
    action_files = list((vault / "Needs_Action").glob("*.md"))
    if len(action_files) > 0:
        print(f"  [OK] Verified: {len(action_files)} action file(s) in Needs_Action/")
        return True
    else:
        print("  [FAIL] Action file not found in Needs_Action/")
        return False

def test_orchestrator():
    """Test 5: Test Orchestrator."""
    print("\n" + "=" * 60)
    print("TEST 5: Orchestrator")
    print("=" * 60)
    
    from orchestrator import Orchestrator
    
    vault = Path("AI_Employee_Vault")
    orchestrator = Orchestrator(str(vault))
    print("  [OK] Orchestrator initialized")
    
    # Get items
    items = orchestrator.get_needs_action_items()
    print(f"  [OK] Found {len(items)} item(s) in Needs_Action/")
    
    # Get status
    status = orchestrator.get_status()
    print(f"  [OK] Status: {status['pending_actions']} pending, {status['pending_approval']} approval")
    
    # Update dashboard
    orchestrator.update_dashboard(status)
    print("  [OK] Dashboard updated")
    
    return True

def test_qwen_prompt():
    """Test 6: Test Qwen Prompt Generation."""
    print("\n" + "=" * 60)
    print("TEST 6: Qwen Prompt Generation")
    print("=" * 60)
    
    from orchestrator import Orchestrator
    
    vault = Path("AI_Employee_Vault")
    orchestrator = Orchestrator(str(vault))
    items = orchestrator.get_needs_action_items()
    
    if len(items) > 0:
        prompt = orchestrator.generate_qwen_prompt(items)
        if "Qwen" in prompt or "AI Employee" in prompt:
            print("  [OK] Qwen prompt generated successfully")
            print(f"  [OK] Prompt length: {len(prompt)} characters")
            return True
        else:
            print("  [FAIL] Prompt doesn't contain expected content")
            return False
    else:
        print("  [SKIP] No items to generate prompt for")
        return True

def main():
    """Run all tests."""
    print("\n")
    print("+" + "=" * 58 + "+")
    print("|" + " " * 10 + "BRONZE TIER VERIFICATION TEST" + " " * 19 + "|")
    print("+" + "=" * 58 + "+")
    print()
    
    results = {
        "Imports": test_imports(),
        "Vault Structure": test_vault_structure(),
        "Vault Files": test_vault_files(),
        "File Watcher": test_watcher(),
        "Orchestrator": test_orchestrator(),
        "Qwen Prompt": test_qwen_prompt(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {test}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED! Bronze Tier is working correctly.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please review the errors above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

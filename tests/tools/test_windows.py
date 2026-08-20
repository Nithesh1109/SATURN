from saturn.tools.base import ToolContext
from saturn.tools.registry import ToolRegistry
from saturn.tools.windows import (
    CloseApplicationTool,
    CopyFileTool,
    CreateFileTool,
    CreateFolderTool,
    DeleteFileTool,
    LockComputerTool,
    MoveFileTool,
    ShutdownComputerTool,
    WindowsToolSet,
)


def test_windows_tool_set_has_expected_tools() -> None:
    names = {tool.name for tool in WindowsToolSet.create()}
    assert names == {
        "open_application", "close_application", "create_folder", "create_file",
        "copy_file", "move_file", "delete_file", "get_clipboard",
        "lock_computer", "shutdown_computer",
    }


def test_registry_can_register_windows_tools() -> None:
    registry = ToolRegistry()
    for tool in WindowsToolSet.create():
        registry.register(tool)
    assert len(registry.names()) == 10


def test_create_folder(tmp_path) -> None:
    path = tmp_path / "nested" / "folder"
    result = CreateFolderTool().execute({"path": str(path)}, ToolContext())
    assert result.success is True
    assert path.is_dir()


def test_create_file(tmp_path) -> None:
    path = tmp_path / "hello.txt"
    result = CreateFileTool().execute(
        {"path": str(path), "content": "hello SATURN"}, ToolContext()
    )
    assert result.success is True
    assert path.read_text(encoding="utf-8") == "hello SATURN"


def test_copy_and_move_file(tmp_path) -> None:
    source = tmp_path / "source.txt"
    copied = tmp_path / "copied.txt"
    moved = tmp_path / "moved.txt"
    source.write_text("SATURN", encoding="utf-8")

    assert CopyFileTool().execute({"source": str(source), "destination": str(copied)}, ToolContext()).success
    assert copied.read_text(encoding="utf-8") == "SATURN"
    assert MoveFileTool().execute({"source": str(copied), "destination": str(moved)}, ToolContext()).success
    assert moved.read_text(encoding="utf-8") == "SATURN"


def test_delete_file(tmp_path) -> None:
    path = tmp_path / "delete.txt"
    path.write_text("x", encoding="utf-8")
    assert DeleteFileTool().execute({"path": str(path)}, ToolContext()).success
    assert not path.exists()


def test_shutdown_requires_confirmation() -> None:
    result = ShutdownComputerTool().execute({}, ToolContext())
    assert result.success is False
    assert "confirmation" in (result.error or "")


def test_lock_tool_contract() -> None:
    assert LockComputerTool().name == "lock_computer"


def test_close_requires_application() -> None:
    result = CloseApplicationTool().execute({}, ToolContext())
    assert result.success is False
    assert "application" in (result.error or "")

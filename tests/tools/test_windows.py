from saturn.tools.base import ToolContext
from saturn.tools.registry import ToolRegistry
from saturn.tools.windows import CreateFileTool, CreateFolderTool, WindowsToolSet


def test_windows_tool_set_has_expected_initial_tools() -> None:
    names = {tool.name for tool in WindowsToolSet.create()}
    assert names == {"open_application", "create_folder", "create_file", "get_clipboard"}


def test_registry_can_register_windows_tools() -> None:
    registry = ToolRegistry()
    for tool in WindowsToolSet.create():
        registry.register(tool)
    assert registry.names() == (
        "create_file",
        "create_folder",
        "get_clipboard",
        "open_application",
    )


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

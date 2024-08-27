<div align="center">
  <center><h1>todo-script</h1></center>
</div>

<br/>

<p align="center">
    <img src="https://raw.githubusercontent.com/Jorgedavyd/todo-script/main/source/logo.png" height=450 width=450>
</p>

todo-script is a basic script that integrates inline TODOs from projects and obsidian tasks. It proposes an easy to use framework based on the Eisenhower-Matrix for task management.
# Features
1. Partial integration with [Tasks](https://publish.obsidian.md/tasks/Introduction).
2. LLM integration for ideas and implementations.
3. RAG informed models for each project.
4. Code visualization in obsidian note.

# How to use
1. Declare the task as a comment on your code in one line.
```cpp
__global__ void KernelDeclaration(void) {
    const unsigned int tid = threadIdx.x + blockIdx.x * blockDim.x; //TODO 080924 low Probably not valid parameter, look for the right descriptor.
    //...
};
```
2. Write your file with the declared `<leader>w` in Setup.

Now you'll be able to see this task in your obsidian project management environment in `<vault_path>/projects/<project_name>` with an LLM inference based on your codebase and a preview of a chunk of code.

# Setup for NeoVim / Vim
1. Clone the script to /usr/bin.

```bash
cd /usr/bin/
git clone https://github.com/Jorgedavyd/todo-script.git
```

2. Add the following nonrecursive remap to nvim/vim.

```lua
vim.keymap.set("n", "<leader>w", function()
    vim.cmd("w")
    local obsidian_vault_project_path = '/path/to/obsidian_vault'  -- Replace with your Obsidian vault path
    -- Save the current buffer
    local project_path = '/path/to/project'  -- Replace with your project path
    local current_file = vim.fn.expand("%")  -- Get the current file path
    local command = string.format(
        "todo-script --filepath %s --obsidian_vault_path %s --project_path %s",
        current_file,
        obsidian_vault_project_path,
        project_path
    )
    vim.cmd("silent !" .. command)
end, { noremap = true, silent = true })
```
If you want to map a template inline task:

```lua
vim.keymap.set("n", "<leader>/", function()
    local date = os.date("%d%m%y")
    local priority = "[P1]"
    local description = "Description here"
    local filetype = vim.bo.filetype
    local comment_chars = {
        lua = "--",
        python = "#",
        html = "<!--",
        css = "/*",
        json = "//",
        markdown = "<!--",
        -- Add more filetypes and their comment characters as needed
    }
    local comment_char = comment_chars[filetype] or "//"
    local todo_template = string.format(
        "%s TODO %s %s %s",
        comment_char,
        date,
        priority,
        description
    )
    local line_num = vim.fn.line(".")
    local line_content = vim.fn.getline(line_num)
    vim.fn.setline(line_num, line_content .. " " .. todo_template)
end, { noremap = true, silent = true })
```
Now, every time you hit the `<leader>w` you'll be analyzing the current file for new tasks, uploading them to the respective obsidian project file with the corresponding solution of the RAG-based language model.

## Contact

- [Linkedin](https://www.linkedin.com/in/jorge-david-enciso-mart%C3%ADnez-149977265/)
- [GitHub](https://github.com/Jorgedavyd)
- Email: jorged.encyso@gmail.com


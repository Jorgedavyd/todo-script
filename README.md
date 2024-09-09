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
Note that the format should be as follows:

`TODO {DATE:ddmmyy} {PRIORITY} {DESC}`

replacing `{PARAM}` with the actual value.

2. Write/Save your file.

Now you'll be able to see this task in your obsidian project management environment in `<vault_path>/projects/<project_name>` with an LLM inference based on your codebase and a preview of a chunk of code.

# Setup
1. Clone the script to `/usr/bin/` or wherever you want, default config is adapted to `/usr/bin/`.

```bash
cd /usr/bin/
git clone https://github.com/Jorgedavyd/todo-script.git
```

2. Add the following service to `systemctl` or use your default task manager to activate the `todoScript.py` script.

```bash
mv todo-script/service/todo-script.service /etc/systemd/system
sudo systemctl start todo-script/service/todo-script.service
sudo systemctl enable todo-script/service/todo-script.service
```

Note that the `todo-script.service` file holds an `{{USER_PLACEHOLDER}}` that should be replaced with your actual username. Change the launching parameters of `todoScript.py` (in the code) given your installation directory and personal file tree settings, the description for each parameter is next to each variable definition as a comment.

## Neovim / Vim automation
If you want to map a template inline task:

```lua
vim.keymap.set("n", "<leader>/", function()
    local date = os.date("%d%m%y")
    local priority = "[P1]"
    local description = "[D1]"
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

## Contact

- [Linkedin](https://www.linkedin.com/in/jorge-david-enciso-mart%C3%ADnez-149977265/)
- [GitHub](https://github.com/Jorgedavyd)
- Email: jorged.encyso@gmail.com


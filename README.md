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
vim.keymap.set("n", "<leader>w", "<cmd>w<CR><cmd>silent !todo-script %<CR>")
```

Now, every time you hit the `<leader>w` you'll be analyzing the current file for new tasks, uploading them to the respective obsidian project file with the corresponding solution of the RAG-based language model.

## Contact

- [Linkedin](https://www.linkedin.com/in/jorge-david-enciso-mart%C3%ADnez-149977265/)
- [GitHub](https://github.com/Jorgedavyd)
- Email: jorged.encyso@gmail.com


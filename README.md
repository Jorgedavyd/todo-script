<center> <h1>todo-scripts</h1> </center>

<p align="center">
    <img src="https://raw.githubusercontent.com/Jorgedavyd/todo-script/main/source/logo.png" height=450 width=450>
</p>

todo-script is a basic script that integrates inline TODOs from projects and obsidian tasks. It proposes an easy to use framework based on the Eisenhower-Matrix for task management.
# Features
1. Partial integration with [Tasks](https://publish.obsidian.md/tasks/Introduction).
2. LLM integration for ideas and implementations.
3. RAG informed models for each project.
4. Code visualization in obsidian note.

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


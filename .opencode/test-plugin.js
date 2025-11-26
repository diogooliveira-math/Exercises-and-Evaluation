// test-plugin.js
import plugin from "./index.ts";

async function testPlugin() {
  try {
    const ctx = {
      client: null,
      project: { id: "test" },
      directory: "c:\\Users\\diogo\\AAA\\Projects\\Exercises and Evaluation",
      worktree: "c:\\Users\\diogo\\AAA\\Projects\\Exercises and Evaluation",
      $: null
    };

    const hooks = await plugin(ctx);
    console.log("Plugin loaded successfully!");
    console.log("Available tools:", Object.keys(hooks.tool || {}));
  } catch (error) {
    console.error("Plugin failed to load:", error);
  }
}

testPlugin();
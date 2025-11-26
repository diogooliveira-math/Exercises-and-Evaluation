// .opencode/index.ts
import addExerciseTool from "./tool/add_exercise_with_types"
import addExerciseSimple from "./tool/add_exercise_simple"
import testTool from "./tool/test_tool"

export default async (ctx) => {
  return {
    tool: {
      add_exercise_with_types: addExerciseTool,
      add_exercise_simple: addExerciseSimple,
      test_tool: testTool,
    },
  }
}
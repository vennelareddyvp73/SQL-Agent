from langgraph.prebuilt import ToolNode


class SQLToolNode:

    def __init__(self, tools):

        self.node = ToolNode(tools)

    def __call__(self, state):
        print(f"\n--- [Tool Node] Executing tool calls... ---")
        result = self.node.invoke(state)
        print(f" -> Tool execution completed.")
        return result
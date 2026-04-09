import asyncio
import os
import json
import re
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage

load_dotenv()

# ====================== MODEL ======================
model = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# ====================== MCP SERVER ======================
server_params = StdioServerParameters(
    command="npx",
    env={
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY"),
    },
    args=["firecrawl-mcp"]
)

# ====================== CORRECTEUR D'APPELS D'OUTILS ======================
def extract_tool_correctly(ai_message: AIMessage) -> list:
    """
    Extrait et corrige les appels d'outils mal formatés par llama-4-scout
    """
    tool_calls = []

    # Si déjà bien formaté
    if hasattr(ai_message, 'tool_calls') and ai_message.tool_calls:
        return ai_message.tool_calls

    content = ai_message.content if hasattr(ai_message, 'content') else str(ai_message)

    # Chercher des patterns d'appels d'outils dans le texte
    # Pattern 1: {"name": "firecrawl_scrape", "arguments": {...}}
    pattern1 = r'\{"name":\s*"([^"]+)",\s*"arguments":\s*(\{[^}]+\})\}'
    matches = re.findall(pattern1, content, re.DOTALL)

    for tool_name, args_str in matches:
        try:
            args = json.loads(args_str)
            tool_calls.append({
                "name": tool_name,
                "args": args,
                "id": f"call_{len(tool_calls)}"
            })
        except:
            pass

    # Pattern 2: firecrawl_scrape(url="...", formats=[...])
    pattern2 = r'firecrawl_scrape\(([^)]+)\)'
    matches = re.findall(pattern2, content)

    for match in matches:
        try:
            # Parser les arguments style key=value
            args = {}
            for param in match.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    if value.startswith('['):
                        value = json.loads(value.replace("'", '"'))
                    args[key] = value
            tool_calls.append({
                "name": "firecrawl_scrape",
                "args": args,
                "id": f"call_{len(tool_calls)}"
            })
        except:
            pass

    return tool_calls

# ====================== AGENT PERSONNALISÉ ======================
class FixedAgent:
    def __init__(self, model, tools):
        self.model = model.bind_tools(tools)
        self.tools = {tool.name: tool for tool in tools}
        self.tool_node = ToolNode(tools)

    async def ainvoke(self, inputs):
        messages = inputs["messages"]

        # Appel au modèle
        response = await self.model.ainvoke(messages)

        # Extraire et corriger les tool calls
        tool_calls = extract_tool_correctly(response)

        # Si pas de tool calls, retourner directement
        if not tool_calls:
            return {"messages": messages + [response]}

        # Créer un AIMessage avec les tool calls corrigés
        corrected_ai = AIMessage(
            content=response.content,
            tool_calls=tool_calls
        )

        # Exécuter les outils
        new_messages = [corrected_ai]
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            if tool_name in self.tools:
                try:
                    result = await self.tools[tool_name].ainvoke(tool_args)
                    new_messages.append(ToolMessage(
                        content=str(result)[:2000],  # Limiter la taille
                        tool_call_id=tool_call["id"]
                    ))
                except Exception as e:
                    new_messages.append(ToolMessage(
                        content=f"Erreur: {str(e)}",
                        tool_call_id=tool_call["id"]
                    ))

        # Appel final au modèle avec les résultats des outils
        final_response = await self.model.ainvoke(messages + new_messages)

        return {"messages": messages + new_messages + [final_response]}

# ====================== MESSAGE MANAGER ======================
class MessageManager:
    def __init__(self, system_prompt, max_messages=4):
        self.messages = [SystemMessage(content=system_prompt)]
        self.max_messages = max_messages

    def add_user_message(self, content):
        self.messages.append(HumanMessage(content=content[:1000]))
        self._trim_history()

    def add_assistant_message(self, content):
        self.messages.append(AIMessage(content=content[:1000]))
        self._trim_history()

    def _trim_history(self):
        if len(self.messages) > self.max_messages + 1:
            kept = [self.messages[0]] + self.messages[-(self.max_messages):]
            self.messages = kept

    def get_messages(self):
        return self.messages

    def clear_except_system(self):
        system_msg = self.messages[0]
        self.messages = [system_msg]

# ====================== MAIN ======================
async def main():
    print("🚀 Démarrage de l'agent MCP (avec correction des tool calls)...")
    print("-" * 60)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)

            print("\n📦 Outils disponibles:")
            for tool in tools:
                print(f"  ✓ {tool.name}")
            print("-" * 60)

            # Utiliser l'agent personnalisé au lieu de create_react_agent
            agent = FixedAgent(model, tools)

            system_prompt = (
                "You are a helpful assistant. Be very concise.\n"
                "To scrape a website, use: firecrawl_scrape(url=\"...\", formats=[\"markdown\"], onlyMainContent=True)\n"
                "Respond briefly."
            )

            msg_manager = MessageManager(system_prompt, max_messages=4)

            print("\n✅ Agent prêt! Tape 'quit' pour quitter.\n")

            while True:
                try:
                    user_input = input("You: ").strip()

                    if user_input.lower() in ["quit", "exit", "q"]:
                        print("Goodbye! 👋")
                        break

                    if not user_input:
                        continue

                    msg_manager.add_user_message(user_input)

                    try:
                        result = await agent.ainvoke({"messages": msg_manager.get_messages()})
                        ai_message = result["messages"][-1].content

                        print(f"\nAgent: {ai_message[:800]}")
                        msg_manager.add_assistant_message(ai_message)

                    except Exception as e:
                        error_msg = str(e)

                        if "rate_limit" in error_msg.lower() or "413" in error_msg:
                            print("\n⚠️ Limite de tokens - pause de 3 secondes...")
                            await asyncio.sleep(3)
                            msg_manager.clear_except_system()

                        elif "400" in error_msg or "tool_use_failed" in error_msg:
                            print("\n⚠️ Erreur d'outil - l'agent va réessayer...")
                            # Nettoyer et réessayer
                            msg_manager.clear_except_system()
                            msg_manager.add_user_message(user_input + " (use firecrawl_scrape directly)")

                        else:
                            print(f"\n❌ Erreur: {error_msg[:200]}")
                            msg_manager.clear_except_system()

                except KeyboardInterrupt:
                    print("\n\nAu revoir! 👋")
                    break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nFermeture propre...")
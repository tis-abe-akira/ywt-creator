from typing import Annotated, Any
import operator
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langchain_core.output_parsers import StrOutputParser

# データモデル
class Persona(BaseModel):
    name: str = Field(..., description="ペルソナの名前")
    background: str = Field(..., description="ペルソナの背景")

class YWTAnalysis(BaseModel):
    y_done: str = Field(..., description="やったこと(Y)の分析")
    w_learned: str = Field(..., description="わかったこと(W)の分析")
    t_next: str = Field(..., description="つぎにやること(T)の分析")

class PersonaAnalysis(BaseModel):
    persona: Persona = Field(..., description="ペルソナ情報")
    analysis: YWTAnalysis = Field(..., description="YWT分析結果")

# ワークフローの状態を管理するクラス
class AnalysisState(BaseModel):
    topic: str = Field(..., description="分析対象のトピック")
    personas: Annotated[list[Persona], operator.add] = Field(
        default_factory=list, description="生成されたペルソナのリスト"
    )
    analyses: Annotated[list[PersonaAnalysis], operator.add] = Field(
        default_factory=list, description="各ペルソナのYWT分析結果"
    )
    current_persona_index: int = Field(default=0, description="現在処理中のペルソナのインデックス")
    is_complete: bool = Field(default=False, description="全ペルソナの分析が完了したかどうか")

# ペルソナ生成クラス
class PersonaGenerator:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
    def generate(self, topic: str) -> list[Persona]:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "あなたは多様なバックグラウンドを持つペルソナを生成する専門家です。"
                "年齢、性別、職業、経験が異なる5人のペルソナを生成してください。"
            ),
            (
                "human",
                "以下のトピックについて分析を行うペルソナを生成してください：\n{topic}"
            )
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        personas_raw = chain.invoke({"topic": topic})
        
        # 生成されたテキストをペルソナオブジェクトに変換
        personas = []
        for i, persona_text in enumerate(personas_raw.split('\n\n')[:5]):
            personas.append(
                Persona(
                    name=f"ペルソナ{i+1}",
                    background=persona_text.strip()
                )
            )
        return personas

# YWT分析クラス
class YWTAnalyzer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm.with_structured_output(YWTAnalysis)
        
    def analyze(self, topic: str, persona: Persona) -> YWTAnalysis:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                f"あなたは以下のペルソナとして分析を行います：\n{persona.name} - {persona.background}"
            ),
            (
                "human",
                "以下のトピックについて、YWTフレームワークを使って分析してください：\n\n"
                "トピック: {topic}\n\n"
                "以下の3つの観点から、このペルソナの視点で分析してください：\n"
                "1. やったこと(Y): これまでに実施した具体的な行動や経験\n"
                "2. わかったこと(W): その経験から得られた気づきや学び\n"
                "3. つぎにやること(T): 今後実施したい具体的なアクション"
            )
        ])
        
        chain = prompt | self.llm
        return chain.invoke({"topic": topic})

# メインの分析エージェント
class MultiPersonaYWTAgent:
    def __init__(self, llm: ChatOpenAI):
        self.persona_generator = PersonaGenerator(llm)
        self.ywt_analyzer = YWTAnalyzer(llm)
        self.graph = self._create_graph()
        
    def _create_graph(self) -> StateGraph:
        # グラフの初期化
        workflow = StateGraph(AnalysisState)
        
        # ノードの追加
        workflow.add_node("generate_personas", self._generate_personas)
        workflow.add_node("analyze_persona", self._analyze_persona)
        workflow.add_node("check_completion", self._check_completion)
        
        # エントリーポイントの設定
        workflow.set_entry_point("generate_personas")
        
        # エッジの設定
        workflow.add_edge("generate_personas", "analyze_persona")
        workflow.add_edge("analyze_persona", "check_completion")
        
        # 条件付きエッジの追加
        workflow.add_conditional_edges(
            "check_completion",
            self._should_continue_analysis,
            {
                True: "analyze_persona",
                False: END
            }
        )
        
        return workflow.compile()
    
    def _generate_personas(self, state: AnalysisState) -> dict[str, Any]:
        personas = self.persona_generator.generate(state.topic)
        return {"personas": personas}
    
    def _analyze_persona(self, state: AnalysisState) -> dict[str, Any]:
        current_persona = state.personas[state.current_persona_index]
        analysis = self.ywt_analyzer.analyze(state.topic, current_persona)
        
        return {
            "analyses": [PersonaAnalysis(persona=current_persona, analysis=analysis)],
            "current_persona_index": state.current_persona_index + 1
        }
    
    def _check_completion(self, state: AnalysisState) -> dict[str, Any]:
        is_complete = state.current_persona_index >= len(state.personas)
        return {"is_complete": is_complete}
    
    def _should_continue_analysis(self, state: AnalysisState) -> bool:
        return not state.is_complete
    
    def run(self, topic: str) -> list[PersonaAnalysis]:
        # 初期状態の設定
        initial_state = AnalysisState(topic=topic)
        # グラフの実行
        final_state = self.graph.invoke(initial_state)
        # 分析結果の取得
        return final_state["analyses"]

def main():
    import argparse
    import os
    from dotenv import load_dotenv
    
    # .envファイルから環境変数を読み込む
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="複数のペルソナによるYWT分析を実行します"
    )
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="分析したいトピックを入力してください"
    )
    
    args = parser.parse_args()
    
    # 分析の実行
    llm = ChatOpenAI(model="gpt-4", temperature=0.0)
    agent = MultiPersonaYWTAgent(llm)
    results = agent.run(args.topic)
    
    # 結果の表示
    for analysis in results:
        print(f"\n=== {analysis.persona.name} ===")
        print(f"背景: {analysis.persona.background}\n")
        print("【やったこと(Y)】")
        print(analysis.analysis.y_done)
        print("\n【わかったこと(W)】")
        print(analysis.analysis.w_learned)
        print("\n【つぎにやること(T)】")
        print(analysis.analysis.t_next)
        print("\n" + "="*50)

if __name__ == "__main__":
    main()

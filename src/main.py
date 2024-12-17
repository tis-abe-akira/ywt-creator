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

class SummaryAnalysis(BaseModel):
    y_summary: str = Field(..., description="やったこと(Y)の総合分析")
    w_summary: str = Field(..., description="わかったこと(W)の総合分析")
    t_summary: str = Field(..., description="つぎにやること(T)の総合分析")

# ワークフローの状態を管理するクラス
class AnalysisState(BaseModel):
    topic: str = Field(..., description="分析対象のトピック")
    personas: Annotated[list[Persona], operator.add] = Field(
        default_factory=list, description="生成されたペルソナのリスト"
    )
    analyses: Annotated[list[PersonaAnalysis], operator.add] = Field(
        default_factory=list, description="各ペルソナのYWT分析結果"
    )
    summary: SummaryAnalysis | None = Field(default=None, description="総合分析結果")
    current_persona_index: int = Field(default=0, description="現在処理中のペルソナのインデックス")
    is_complete: bool = Field(default=False, description="全ペルソナの分析が完了したかどうか")

# ログ出力用の関数
def print_progress(message: str, is_state: bool = False):
    if is_state:
        print("\n🔄 State:", message)
    else:
        print("📝", message)
    
def print_section(title: str):
    print(f"\n{'='*20} {title} {'='*20}")

def get_persona_summary(persona: Persona) -> str:
    # ペルソナの背景から最初の文を抽出（通常、役割や立場を示す部分）
    first_sentence = persona.background.split('.')[0]
    return f"{persona.name}（{first_sentence}）"

def get_analysis_summary(analysis: YWTAnalysis) -> str:
    # 各セクションの最初の文を抽出してサマリーを作成
    y_summary = analysis.y_done.split('.')[0]
    w_summary = analysis.w_learned.split('.')[0]
    t_summary = analysis.t_next.split('.')[0]
    return f"Y: {y_summary}... W: {w_summary}... T: {t_summary}..."

# ペルソナ生成クラス
class PersonaGenerator:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
    def generate(self, topic: str) -> list[Persona]:
        print_progress("ペルソナを生成中...")
        
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
            persona = Persona(
                name=f"ペルソナ{i+1}",
                background=persona_text.strip()
            )
            print_progress(f"ペルソナ{i+1}を生成しました → {get_persona_summary(persona)}")
            personas.append(persona)
        
        return personas

# YWT分析クラス
class YWTAnalyzer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm.with_structured_output(YWTAnalysis)
        
    def analyze(self, topic: str, persona: Persona) -> YWTAnalysis:
        print_progress(f"{persona.name}のYWT分析を実行中...")
        
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
        analysis = chain.invoke({"topic": topic})
        print_progress(f"{persona.name}のYWT分析が完了しました → {get_analysis_summary(analysis)}")
        return analysis

# 総合分析クラス
class SummaryAnalyzer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm.with_structured_output(SummaryAnalysis)
    
    def analyze(self, topic: str, analyses: list[PersonaAnalysis]) -> SummaryAnalysis:
        print_progress("全ペルソナの分析結果を総合分析中...")
        
        # 各ペルソナの分析をまとめて文字列化
        analyses_text = "\n\n".join([
            f"背景: {analysis.persona.background}\n"
            f"やったこと(Y): {analysis.analysis.y_done}\n"
            f"わかったこと(W): {analysis.analysis.w_learned}\n"
            f"つぎにやること(T): {analysis.analysis.t_next}"
            for analysis in analyses
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "あなたは複数の視点からの分析を総合し、より深い洞察を導き出す専門家です。"
                "単なる要約ではなく、異なる視点からの意見を統合して、新しい知見や示唆を見出すことが求められています。"
                "\n\n"
                "以下の点に注意して分析を行ってください：\n"
                "1. 個々の意見の単なる要約は避け、全体を俯瞰した深い考察を行う\n"
                "2. 異なる背景や経験レベルからの視点を統合し、普遍的な知見を見出す\n"
                "3. 表面的な共通点だけでなく、根底にある本質的な要素を抽出する\n"
                "4. 対立する意見がある場合は、その背景にある理由を考察する\n"
                "5. 個々の経験や知見を組み合わせることで得られる新しい示唆を導き出す"
            ),
            (
                "human",
                "以下のトピックに関する複数の分析結果を総合的に分析し、"
                "より深い洞察と本質的な示唆を導き出してください：\n\n"
                "トピック: {topic}\n\n"
                "各分析結果:\n{analyses}\n\n"
                "YWTフレームワークの各観点で総合的な分析を行い、以下の点を含めてください：\n"
                "1. やったこと(Y): 様々な取り組みや経験から見出される本質的なアプローチや効果的な学習パターン\n"
                "2. わかったこと(W): 異なる視点からの気づきを統合して得られる普遍的な知見や重要な示唆\n"
                "3. つぎにやること(T): 多様な経験と学びを踏まえた、より効果的で包括的なアクションプラン"
            )
        ])
        
        chain = prompt | self.llm
        summary = chain.invoke({
            "topic": topic,
            "analyses": analyses_text
        })
        
        # 総合分析の主要ポイントを表示
        print_progress("総合分析が完了しました")
        print_progress("主要な発見:")
        print_progress(f"・やったこと(Y): {summary.y_summary.split('.')[0]}...")
        print_progress(f"・わかったこと(W): {summary.w_summary.split('.')[0]}...")
        print_progress(f"・つぎにやること(T): {summary.t_summary.split('.')[0]}...")
        
        return summary

# メインの分析エージェント
class MultiPersonaYWTAgent:
    def __init__(self, llm: ChatOpenAI):
        self.persona_generator = PersonaGenerator(llm)
        self.ywt_analyzer = YWTAnalyzer(llm)
        self.summary_analyzer = SummaryAnalyzer(llm)
        self.graph = self._create_graph()
        
    def _create_graph(self) -> StateGraph:
        # グラフの初期化
        workflow = StateGraph(AnalysisState)
        
        # ノードの追加
        workflow.add_node("generate_personas", self._generate_personas)
        workflow.add_node("analyze_persona", self._analyze_persona)
        workflow.add_node("check_completion", self._check_completion)
        workflow.add_node("create_summary", self._create_summary)
        
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
                False: "create_summary"
            }
        )
        
        workflow.add_edge("create_summary", END)
        
        return workflow.compile()
    
    def _generate_personas(self, state: AnalysisState) -> dict[str, Any]:
        print_section("ペルソナ生成フェーズ")
        print_progress(f"分析トピック: {state.topic}", is_state=True)
        personas = self.persona_generator.generate(state.topic)
        return {"personas": personas}
    
    def _analyze_persona(self, state: AnalysisState) -> dict[str, Any]:
        if state.current_persona_index == 0:
            print_section("ペルソナ分析フェーズ")
        
        current_persona = state.personas[state.current_persona_index]
        print_progress(f"現在の分析対象: {get_persona_summary(current_persona)}", is_state=True)
        
        analysis = self.ywt_analyzer.analyze(state.topic, current_persona)
        
        return {
            "analyses": [PersonaAnalysis(persona=current_persona, analysis=analysis)],
            "current_persona_index": state.current_persona_index + 1
        }
    
    def _check_completion(self, state: AnalysisState) -> dict[str, Any]:
        is_complete = state.current_persona_index >= len(state.personas)
        if is_complete:
            print_progress("全ペルソナの分析が完了しました", is_state=True)
        return {"is_complete": is_complete}
    
    def _should_continue_analysis(self, state: AnalysisState) -> bool:
        return not state.is_complete
    
    def _create_summary(self, state: AnalysisState) -> dict[str, Any]:
        print_section("総合分析フェーズ")
        summary = self.summary_analyzer.analyze(state.topic, state.analyses)
        return {"summary": summary}
    
    def run(self, topic: str) -> tuple[list[PersonaAnalysis], SummaryAnalysis]:
        print_section("分析開始")
        print_progress(f"トピック: {topic}")
        
        # 初期状態の設定
        initial_state = AnalysisState(topic=topic)
        # グラフの実行
        final_state = self.graph.invoke(initial_state)
        
        print_section("分析完了")
        # 分析結果の取得
        return final_state["analyses"], final_state["summary"]

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
    results, summary = agent.run(args.topic)
    
    # 結果の表示
    print_section("個別分析結果")
    
    # 個別の分析結果の表示
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
    
    # 総合分析の表示
    print_section("総合分析結果")
    print("\n【やったことの総合分析(Y)】")
    print(summary.y_summary)
    print("\n【わかったことの総合分析(W)】")
    print(summary.w_summary)
    print("\n【つぎにやることの総合分析(T)】")
    print(summary.t_summary)
    print("\n" + "="*50)

if __name__ == "__main__":
    main()

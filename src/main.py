from typing import Annotated, Any, Literal
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


class YAnalysis(BaseModel):
    y_done: str = Field(..., description="やったこと(Y)の分析")


class WAnalysis(BaseModel):
    w_learned: str = Field(..., description="わかったこと(W)の分析")


class TAnalysis(BaseModel):
    t_next: str = Field(..., description="つぎにやること(T)の分析")


class PersonaAnalysis(BaseModel):
    persona: Persona = Field(..., description="ペルソナ情報")
    y_analysis: YAnalysis | None = Field(default=None, description="Y分析結果")
    w_analysis: WAnalysis | None = Field(default=None, description="W分析結果")
    t_analysis: TAnalysis | None = Field(default=None, description="T分析結果")


class StepSummary(BaseModel):
    summary: str = Field(..., description="ステップの総合分析")


# ワークフローの状態を管理するクラス
class AnalysisState(BaseModel):
    topic: str = Field(..., description="分析対象のトピック")
    personas: Annotated[list[Persona], operator.add] = Field(
        default_factory=list, description="生成されたペルソナのリスト"
    )
    analyses: dict[str, PersonaAnalysis] = Field(
        default_factory=dict, description="各ペルソナの分析結果"
    )
    current_step: Literal["Y", "W", "T"] = Field(
        default="Y", description="現在の分析ステップ"
    )
    current_persona_index: int = Field(
        default=0, description="現在処理中のペルソナのインデックス"
    )
    y_summary: StepSummary | None = Field(default=None, description="Yの総合分析")
    w_summary: StepSummary | None = Field(default=None, description="Wの総合分析")
    t_summary: StepSummary | None = Field(default=None, description="Tの総合分析")
    is_complete: bool = Field(default=False, description="全ての分析が完了したかどうか")


# ログ出力用の関数
def print_progress(message: str, is_state: bool = False):
    if is_state:
        print("\n🔄 State:", message)
    else:
        print("📝", message)


def print_section(title: str):
    print(f"\n{'='*20} {title} {'='*20}")


def get_persona_summary(persona: Persona) -> str:
    first_sentence = persona.background.split(".")[0]
    return f"{persona.name}（{first_sentence}）"


# ペルソナ生成クラス
class PersonaGenerator:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def generate(self, topic: str) -> list[Persona]:
        print_progress("ペルソナを生成中...")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは多様なバックグラウンドを持つペルソナを生成する専門家です。"
                    "年齢、性別、職業、経験が異なる5人のペルソナを生成してください。",
                ),
                (
                    "human",
                    "以下のトピックについて分析を行うペルソナを生成してください：\n{topic}",
                ),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        personas_raw = chain.invoke({"topic": topic})

        personas = []
        for i, persona_text in enumerate(personas_raw.split("\n\n")[:3]):
            persona = Persona(name=f"ペルソナ{i+1}", background=persona_text.strip())
            print_progress(
                f"ペルソナ{i+1}を生成しました → {get_persona_summary(persona)}"
            )
            personas.append(persona)

        return personas


# YWT分析クラス
class YWTAnalyzer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def analyze_y(self, topic: str, persona: Persona) -> YAnalysis:
        print_progress(f"{persona.name}のY分析を実行中...")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"あなたは以下のペルソナとして分析を行います：\n{persona.name} - {persona.background}",
                ),
                (
                    "human",
                    "以下のトピックについて分析してください：\n\n"
                    "トピック: {topic}\n\n"
                    "【やったこと(Y)】\n"
                    "これまでに実施した具体的な行動や経験を詳しく説明してください。",
                ),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        y_done = chain.invoke({"topic": topic})
        analysis = YAnalysis(y_done=y_done)

        print_progress(
            f"{persona.name}のY分析が完了しました → {y_done.split('.')[0]}..."
        )
        return analysis

    def analyze_w(
        self, topic: str, persona: Persona, y_analysis: YAnalysis
    ) -> WAnalysis:
        print_progress(f"{persona.name}のW分析を実行中...")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"あなたは以下のペルソナとして分析を行います：\n{persona.name} - {persona.background}\n\n"
                    f"このペルソナの「やったこと(Y)」は以下の通りです：\n{y_analysis.y_done}",
                ),
                (
                    "human",
                    "以下のトピックについて分析してください：\n\n"
                    "トピック: {topic}\n\n"
                    "【わかったこと(W)】\n"
                    "上記の「やったこと」から得られた気づきや学びを詳しく説明してください。\n"
                    "特に以下の点を意識して分析してください：\n"
                    "1. 具体的な行動や経験から得られた具体的な気づき\n"
                    "2. 予想外の発見や意外な学び\n"
                    "3. 成功や失敗から得られた教訓\n"
                    "4. 今後の行動に活かせる重要な示唆",
                ),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        w_learned = chain.invoke({"topic": topic})
        analysis = WAnalysis(w_learned=w_learned)

        print_progress(
            f"{persona.name}のW分析が完了しました → {w_learned.split('.')[0]}..."
        )
        return analysis

    def analyze_t(
        self, topic: str, persona: Persona, y_analysis: YAnalysis, w_analysis: WAnalysis
    ) -> TAnalysis:
        print_progress(f"{persona.name}のT分析を実行中...")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"あなたは以下のペルソナとして分析を行います：\n{persona.name} - {persona.background}\n\n"
                    f"このペルソナの分析結果は以下の通りです：\n"
                    f"【やったこと(Y)】\n{y_analysis.y_done}\n\n"
                    f"【わかったこと(W)】\n{w_analysis.w_learned}",
                ),
                (
                    "human",
                    "以下のトピックについて分析してください：\n\n"
                    "トピック: {topic}\n\n"
                    "【つぎにやること(T)】\n"
                    "上記の「やったこと」と「わかったこと」を踏まえて、\n"
                    "今後実施したい具体的なアクションを詳しく説明してください。\n"
                    "特に以下の点を意識して分析してください：\n"
                    "1. これまでの経験から得られた学びを活かしたアクション\n"
                    "2. 気づいた課題や改善点に対する具体的な対応策\n"
                    "3. 新たな挑戦や実験的な試み\n"
                    "4. 長期的な成長につながる持続可能な行動計画",
                ),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        t_next = chain.invoke({"topic": topic})
        analysis = TAnalysis(t_next=t_next)

        print_progress(
            f"{persona.name}のT分析が完了しました → {t_next.split('.')[0]}..."
        )
        return analysis


# 総合分析クラス
class StepAnalyzer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def analyze_y_step(
        self, topic: str, analyses: list[tuple[Persona, YAnalysis]]
    ) -> StepSummary:
        print_progress("Yステップの総合分析を実行中...")

        analyses_text = "\n\n".join(
            [
                f"背景: {persona.background}\n" f"やったこと(Y): {analysis.y_done}"
                for persona, analysis in analyses
            ]
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは複数の視点からの分析を総合し、より深い洞察を導き出す専門家です。"
                    "単なる要約ではなく、異なる視点からの経験を統合して、新しい知見や示唆を見出すことが求められています。"
                    "\n\n"
                    "以下の点に注意して分析を行ってください：\n"
                    "1. 個々の経験の単なる要約は避け、全体を俯瞰した深い考察を行う\n"
                    "2. 異なる背景や経験レベルからの視点を統合し、普遍的な知見を見出す\n"
                    "3. 表面的な共通点だけでなく、根底にある本質的な要素を抽出する\n"
                    "4. 対立する経験がある場合は、その背景にある理由を考察する\n"
                    "5. 個々の経験を組み合わせることで得られる新しい示唆を導き出す",
                ),
                (
                    "human",
                    "以下のトピックに関する複数の「やったこと(Y)」の分析結果を総合的に分析し、"
                    "より深い洞察と本質的な示唆を導き出してください：\n\n"
                    "トピック: {topic}\n\n"
                    "各分析結果:\n{analyses}\n\n"
                    "様々な取り組みや経験から見出される本質的なアプローチや効果的な学習パターンを"
                    "抽出し、新しい知見として提示してください。",
                ),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        summary = chain.invoke({"topic": topic, "analyses": analyses_text})

        print_progress("Yステップの総合分析が完了しました")
        print_progress(f"主要な発見: {summary.split('.')[0]}...")

        return StepSummary(summary=summary)

    def analyze_w_step(
        self,
        topic: str,
        analyses: list[tuple[Persona, YAnalysis, WAnalysis]],
        y_summary: StepSummary,
    ) -> StepSummary:
        print_progress("Wステップの総合分析を実行中...")

        analyses_text = "\n\n".join(
            [
                f"背景: {persona.background}\n"
                f"やったこと(Y): {y_analysis.y_done}\n"
                f"わかったこと(W): {w_analysis.w_learned}"
                for persona, y_analysis, w_analysis in analyses
            ]
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは複数の視点からの分析を総合し、より深い洞察を導き出す専門家です。"
                    "単なる要約ではなく、異なる視点からの気づきを統合して、新しい知見や示唆を見出すことが求められています。"
                    "\n\n"
                    "以下の点に注意して分析を行ってください：\n"
                    "1. 個々の気づきの単なる要約は避け、全体を俯瞰した深い考察を行う\n"
                    "2. 異なる背景や経験レベルからの視点を統合し、普遍的な知見を見出す\n"
                    "3. 表面的な共通点だけでなく、根底にある本質的な要素を抽出する\n"
                    "4. 対立する気づきがある場合は、その背景にある理由を考察する\n"
                    "5. 個々の気づきを組み合わせることで得られる新しい示唆を導き出す\n\n"
                    f"「やったこと(Y)」の総合分析結果は以下の通りです：\n{y_summary.summary}",
                ),
                (
                    "human",
                    "以下のトピックに関する複数の「わかったこと(W)」の分析結果を、"
                    "「やったこと(Y)」の総合分析も踏まえて総合的に分析し、"
                    "より深い洞察と本質的な示唆を導き出してください：\n\n"
                    "トピック: {topic}\n\n"
                    "各分析結果:\n{analyses}\n\n"
                    "異なる視点からの気づきを統合して得られる普遍的な知見や重要な示唆を"
                    "抽出し、新しい知見として提示してください。",
                ),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        summary = chain.invoke({"topic": topic, "analyses": analyses_text})

        print_progress("Wステップの総合分析が完了しました")
        print_progress(f"主要な発見: {summary.split('.')[0]}...")

        return StepSummary(summary=summary)

    def analyze_t_step(
        self,
        topic: str,
        analyses: list[tuple[Persona, YAnalysis, WAnalysis, TAnalysis]],
        y_summary: StepSummary,
        w_summary: StepSummary,
    ) -> StepSummary:
        print_progress("Tステップの総合分析を実行中...")

        analyses_text = "\n\n".join(
            [
                f"背景: {persona.background}\n"
                f"やったこと(Y): {y_analysis.y_done}\n"
                f"わかったこと(W): {w_analysis.w_learned}\n"
                f"つぎにやること(T): {t_analysis.t_next}"
                for persona, y_analysis, w_analysis, t_analysis in analyses
            ]
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは複数の視点からの分析を総合し、より深い洞察を導き出す専門家です。"
                    "単なる要約ではなく、異なる視点からの計画を統合して、新しい知見や示唆を見出すことが求められています。"
                    "\n\n"
                    "以下の点に注意して分析を行ってください：\n"
                    "1. 個々の計画の単なる要約は避け、全体を俯瞰した深い考察を行う\n"
                    "2. 異なる背景や経験レベルからの視点を統合し、普遍的な知見を見出す\n"
                    "3. 表面的な共通点だけでなく、根底にある本質的な要素を抽出する\n"
                    "4. 対立する計画がある場合は、その背景にある理由を考察する\n"
                    "5. 個々の計画を組み合わせることで得られる新しい示唆を導き出す\n\n"
                    f"これまでの総合分析結果は以下の通りです：\n\n"
                    f"【やったこと(Y)の総合分析】\n{y_summary.summary}\n\n"
                    f"【わかったこと(W)の総合分析】\n{w_summary.summary}",
                ),
                (
                    "human",
                    "以下のトピックに関する複数の「つぎにやること(T)」の分析結果を、"
                    "「やったこと(Y)」と「わかったこと(W)」の総合分析も踏まえて総合的に分析し、"
                    "より深い洞察と本質的な示唆を導き出してください：\n\n"
                    "トピック: {topic}\n\n"
                    "各分析結果:\n{analyses}\n\n"
                    "多様な経験と学びを踏まえた、より効果的で包括的なアクションプランを"
                    "抽出し、新しい知見として提示してください。",
                ),
            ]
        )

        chain = prompt | self.llm | StrOutputParser()
        summary = chain.invoke({"topic": topic, "analyses": analyses_text})

        print_progress("Tステップの総合分析が完了しました")
        print_progress(f"主要な発見: {summary.split('.')[0]}...")

        return StepSummary(summary=summary)


# メインの分析エージェント
class MultiPersonaYWTAgent:
    def __init__(self, llm: ChatOpenAI):
        self.persona_generator = PersonaGenerator(llm)
        self.ywt_analyzer = YWTAnalyzer(llm)
        self.step_analyzer = StepAnalyzer(llm)
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        # グラフの初期化
        workflow = StateGraph(AnalysisState)

        # ノードの追加
        workflow.add_node("generate_personas", self._generate_personas)
        workflow.add_node("analyze_current_step", self._analyze_current_step)
        workflow.add_node("check_persona_completion", self._check_persona_completion)
        workflow.add_node("summarize_current_step", self._summarize_current_step)
        workflow.add_node("move_to_next_step", self._move_to_next_step)
        workflow.add_node("check_step_completion", self._check_step_completion)

        # エントリーポイントの設定
        workflow.set_entry_point("generate_personas")

        # エッジの設定
        workflow.add_edge("generate_personas", "analyze_current_step")
        workflow.add_edge("analyze_current_step", "check_persona_completion")

        # 条件付きエッジの追加
        workflow.add_conditional_edges(
            "check_persona_completion",
            self._should_continue_persona_analysis,
            {True: "analyze_current_step", False: "summarize_current_step"},
        )

        workflow.add_edge("summarize_current_step", "move_to_next_step")
        workflow.add_edge("move_to_next_step", "check_step_completion")

        workflow.add_conditional_edges(
            "check_step_completion",
            self._should_continue_step_analysis,
            {True: "analyze_current_step", False: END},
        )

        return workflow.compile()

    def _generate_personas(self, state: AnalysisState) -> dict[str, Any]:
        print_section("ペルソナ生成フェーズ")
        print_progress(f"分析トピック: {state.topic}", is_state=True)
        personas = self.persona_generator.generate(state.topic)

        # 分析結果の初期化
        analyses = {}
        for persona in personas:
            analyses[persona.name] = PersonaAnalysis(persona=persona)

        return {"personas": personas, "analyses": analyses}

    def _analyze_current_step(self, state: AnalysisState) -> dict[str, Any]:
        if state.current_persona_index == 0:
            print_section(f"{state.current_step}ステップの分析フェーズ")

        current_persona = state.personas[state.current_persona_index]
        print_progress(
            f"現在の分析対象: {get_persona_summary(current_persona)}", is_state=True
        )

        # 現在のペルソナの分析結果を取得
        current_analysis = state.analyses.get(current_persona.name)
        if current_analysis is None:
            # 分析結果が存在しない場合は新しく作成
            current_analysis = PersonaAnalysis(persona=current_persona)
            state.analyses[current_persona.name] = current_analysis

        if state.current_step == "Y":
            y_analysis = self.ywt_analyzer.analyze_y(state.topic, current_persona)
            current_analysis.y_analysis = y_analysis
        elif state.current_step == "W":
            y_analysis = current_analysis.y_analysis
            if y_analysis is None:
                raise ValueError("Y分析が完了していません")
            w_analysis = self.ywt_analyzer.analyze_w(
                state.topic, current_persona, y_analysis
            )
            current_analysis.w_analysis = w_analysis
        else:  # T
            y_analysis = current_analysis.y_analysis
            w_analysis = current_analysis.w_analysis
            if y_analysis is None or w_analysis is None:
                raise ValueError("YまたはW分析が完了していません")
            t_analysis = self.ywt_analyzer.analyze_t(
                state.topic, current_persona, y_analysis, w_analysis
            )
            current_analysis.t_analysis = t_analysis

        # 更新された分析結果を含む新しい状態を返す
        updated_analyses = state.analyses.copy()
        updated_analyses[current_persona.name] = current_analysis

        return {
            "analyses": updated_analyses,
            "current_persona_index": state.current_persona_index + 1,
        }

    def _check_persona_completion(self, state: AnalysisState) -> dict[str, Any]:
        is_complete = state.current_persona_index >= len(state.personas)
        if is_complete:
            print_progress(
                f"全ペルソナの{state.current_step}分析が完了しました", is_state=True
            )
        return {"is_complete": is_complete}

    def _should_continue_persona_analysis(self, state: AnalysisState) -> bool:
        return not state.is_complete

    def _summarize_current_step(self, state: AnalysisState) -> dict[str, Any]:
        print_section(f"{state.current_step}ステップの総合分析フェーズ")

        if state.current_step == "Y":
            # Y分析の総合
            y_analyses = [
                (persona, state.analyses[persona.name].y_analysis)
                for persona in state.personas
                if state.analyses[persona.name].y_analysis is not None
            ]
            summary = self.step_analyzer.analyze_y_step(state.topic, y_analyses)
            return {"y_summary": summary}

        elif state.current_step == "W":
            # W分析の総合（Yの結果も含める）
            if state.y_summary is None:
                raise ValueError("Y総合分析が完了していません")

            w_analyses = [
                (
                    persona,
                    state.analyses[persona.name].y_analysis,
                    state.analyses[persona.name].w_analysis,
                )
                for persona in state.personas
                if (
                    state.analyses[persona.name].y_analysis is not None
                    and state.analyses[persona.name].w_analysis is not None
                )
            ]
            summary = self.step_analyzer.analyze_w_step(
                state.topic, w_analyses, state.y_summary
            )
            return {"w_summary": summary}

        else:  # T
            # T分析の総合（YとWの結果も含める）
            if state.y_summary is None or state.w_summary is None:
                raise ValueError("YまたはW総合分析が完了していません")

            t_analyses = [
                (
                    persona,
                    state.analyses[persona.name].y_analysis,
                    state.analyses[persona.name].w_analysis,
                    state.analyses[persona.name].t_analysis,
                )
                for persona in state.personas
                if (
                    state.analyses[persona.name].y_analysis is not None
                    and state.analyses[persona.name].w_analysis is not None
                    and state.analyses[persona.name].t_analysis is not None
                )
            ]
            summary = self.step_analyzer.analyze_t_step(
                state.topic, t_analyses, state.y_summary, state.w_summary
            )
            return {"t_summary": summary}

    def _move_to_next_step(self, state: AnalysisState) -> dict[str, Any]:
        next_step = {"Y": "W", "W": "T", "T": "T"}[state.current_step]
        return {"current_step": next_step, "current_persona_index": 0}

    def _check_step_completion(self, state: AnalysisState) -> dict[str, Any]:
        is_complete = state.current_step == "T" and state.t_summary is not None
        return {"is_complete": is_complete}

    def _should_continue_step_analysis(self, state: AnalysisState) -> bool:
        return not state.is_complete

    def run(
        self, topic: str
    ) -> tuple[dict[str, PersonaAnalysis], StepSummary, StepSummary, StepSummary]:
        print_section("分析開始")
        print_progress(f"トピック: {topic}")

        # 初期状態の設定
        initial_state = AnalysisState(topic=topic)
        # グラフの実行
        final_state = self.graph.invoke(initial_state, {"recursion_limit": 100})

        print_section("分析完了")
        # 分析結果の取得
        return (
            final_state["analyses"],
            final_state["y_summary"],
            final_state["w_summary"],
            final_state["t_summary"],
        )


def main():
    print("start")
    import argparse
    import os
    from dotenv import load_dotenv

    # .envファイルから環境変数を読み込む
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="複数のペルソナによるYWT分析を実行します"
    )
    parser.add_argument(
        "--topic", type=str, required=True, help="分析したいトピックを入力してください"
    )

    args = parser.parse_args()

    # 分析の実行
    llm = ChatOpenAI(model="gpt-4", temperature=0.0)
    agent = MultiPersonaYWTAgent(llm)
    analyses, y_summary, w_summary, t_summary = agent.run(args.topic)

    # 結果の表示
    print_section("個別分析結果")

    # 個別の分析結果の表示
    for analysis in analyses.values():
        print(f"\n=== {analysis.persona.name} ===")
        print(f"背景: {analysis.persona.background}\n")
        if analysis.y_analysis:
            print("【やったこと(Y)】")
            print(analysis.y_analysis.y_done)
        if analysis.w_analysis:
            print("\n【わかったこと(W)】")
            print(analysis.w_analysis.w_learned)
        if analysis.t_analysis:
            print("\n【つぎにやること(T)】")
            print(analysis.t_analysis.t_next)
        print("\n" + "=" * 50)

    # 総合分析の表示
    print_section("総合分析結果")
    print("\n【やったことの総合分析(Y)】")
    print(y_summary.summary)
    print("\n【わかったことの総合分析(W)】")
    print(w_summary.summary)
    print("\n【つぎにやることの総合分析(T)】")
    print(t_summary.summary)


if __name__ == "__main__":
    main()

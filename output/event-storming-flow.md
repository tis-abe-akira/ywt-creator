flowchart TD
    start([開始]) --> proposal[改善施策の提案]
    proposal --> feasibility[実行可能性評価]
    feasibility --> roi{IRR評価}
    
    roi -->|IRR >= 5%| compliance[法令・規約チェック]
    roi -->|IRR < 5%| rejected([却下])
    
    compliance --> terms{利用規約への影響}
    terms -->|あり| legal[法務部相談]
    terms -->|なし| approval{承認判断}
    
    legal --> revision{改定必要}
    revision -->|Yes| update[利用規約改定]
    revision -->|No| approval
    
    update --> consent[会員同意取得]
    consent --> approval
    
    approval -->|開発費用>1000万円 or 新規パッケージ| upper[上位組織承認判断]
    approval -->|その他| dev_ready[承認完了]
    
    upper -->|承認| dev_ready
    upper -->|条件付き| condition[条件付き承認]
    upper -->|却下| rejected
    
    condition --> restudy[フィージビリティスタディ]
    restudy --> recheck{条件クリア}
    recheck -->|Yes| dev_ready
    recheck -->|No| rejected
    
    dev_ready --> requirement[要件定義]
    requirement --> development[開発]
    development --> impl[実装完了]
    
    impl --> quality{品質基準}
    quality -->|未達| review[品質保証部レビュー]
    quality -->|達成| release_judge[リリース判定]
    
    review --> release_judge
    
    release_judge -->|承認| release_prep[リリース準備]
    release_judge -->|条件付き| postpone[リリース延期]
    release_judge -->|却下| development
    
    postpone -->|条件クリア| release_prep
    
    release_prep --> release[リリース実施]
    release --> measure[効果測定]
    measure --> feedback[フィードバック]
    feedback --> finish([終了])
    
    rejected --> finish
    
    subgraph 外部システム連携
        CRM[CRMシステム]
        PMS[プロジェクト管理システム]
    end
    
    measure -.-> CRM
    development -.-> PMS
    
    style start fill:#f9f,stroke:#333,stroke-width:2px
    style finish fill:#f9f,stroke:#333,stroke-width:2px
    style rejected fill:#f66,stroke:#333,stroke-width:2px
    
    classDef decision fill:#ffb,stroke:#333,stroke-width:2px
    class roi,terms,revision,approval,quality,release_judge,recheck decision
    
    classDef process fill:#bfb,stroke:#333,stroke-width:2px
    class proposal,feasibility,compliance,legal,update,consent,dev_ready,requirement,development,impl,review,release_prep,release,measure,feedback process
    
    classDef external fill:#ddd,stroke:#333,stroke-width:2px
    class CRM,PMS external

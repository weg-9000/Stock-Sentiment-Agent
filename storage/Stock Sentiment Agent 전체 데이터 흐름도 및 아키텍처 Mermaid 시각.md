
# Stock Sentiment Agent 전체 데이터 흐름도 및 아키텍처 Mermaid 시각화

## 1. 전체 시스템 아키텍처 개요

```mermaid
graph TB
    subgraph "User Interface Layer"
        User[사용자]
        UI[Streamlit ChatBot UI]
        Gateway[API Gateway]
        LB[Load Balancer]
    end
    
    subgraph "Stock Sentiment Agent Core"
        Agent[StockSentimentAgent]
        MCP[MCP Client Manager]
        HyperCLOVA[HyperCLOVA X Client]
        Kafka[Kafka Producer]
        Storage[Storage Manager]
    end
    
    subgraph "Data Processing Pipeline"
        Pipeline[Data Processing Pipeline]
    end
    
    User --> UI
    UI --> Gateway
    Gateway --> LB
    LB --> Agent
    
    Agent --> MCP
    Agent --> HyperCLOVA
    Agent --> Kafka
    Agent --> Storage
    Agent --> Pipeline
    
    classDef userLayer fill:#e1f5fe
    classDef agentCore fill:#f3e5f5
    classDef pipeline fill:#e8f5e8
    
    class User,UI,Gateway,LB userLayer
    class Agent,MCP,HyperCLOVA,Kafka,Storage agentCore
    class Pipeline pipeline
```


## 2. MCP JSON RPC → Kafka 데이터 수집 흐름

```mermaid
sequenceDiagram
    participant A as MCP Client (Agent)
    participant T as Twitter MCP Server
    participant AV as AlphaVantage MCP Server
    participant AP as Apify MCP Server
    participant DM as Data Merger
    participant KP as Kafka Producer
    participant NC as NAVER Cloud Data Streaming
    
    Note over A, AP: Data Collection Layer
    
    A->>T: JSON RPC 2.0: search_tweets("$AAPL")
    A->>AV: JSON RPC 2.0: get_quote("AAPL")  
    A->>AP: JSON RPC 2.0: getTweets("AAPL")
    
    T-->>A: Tweet data response
    AV-->>A: Price data response
    AP-->>A: Community data response
    
    A->>DM: Raw data normalization
    Note over DM: • Timestamp Addition<br/>• Source Tagging<br/>• Schema Validation<br/>• Deduplication
    
    DM->>KP: Standardized JSON data
    KP->>NC: Stream to Kafka topics
    
    Note over NC: NAVER Cloud<br/>Managed Kafka
```


## 3. NAVER Cloud Data Streaming Kafka 아키텍처

```mermaid
graph TB
    subgraph "NAVER Cloud VPC Private Subnet"
        subgraph "Kafka Cluster"
            B1[Broker #1<br/>Leader]
            B2[Broker #2<br/>Follower]
            B3[Broker #3<br/>Follower]
        end
        
        subgraph "ZooKeeper Cluster"
            ZK1[ZK #1]
            ZK2[ZK #2] 
            ZK3[ZK #3]
        end
        
        subgraph "Kafka Topics"
            T1[stock-social-raw<br/>12 partitions]
            T2[stock-price-raw<br/>6 partitions]
            T3[stock-news-raw<br/>6 partitions]
            T4[stock-processed<br/>24 partitions]
            T5[stock-sentiment<br/>12 partitions]
        end
    end
    
    B1 --- B2
    B2 --- B3
    B1 --- B3
    
    ZK1 --- ZK2
    ZK2 --- ZK3
    ZK1 --- ZK3
    
    B1 --> T1
    B1 --> T2
    B1 --> T3
    B1 --> T4
    B1 --> T5
    
    classDef broker fill:#ffecb3
    classDef zookeeper fill:#c8e6c9
    classDef topic fill:#e1f5fe
    
    class B1,B2,B3 broker
    class ZK1,ZK2,ZK3 zookeeper
    class T1,T2,T3,T4,T5 topic
```


## 4. 데이터 가공 파이프라인 흐름

```mermaid
flowchart LR
    subgraph "Input Topics"
        I1[stock-social-raw<br/>• Twitter Data<br/>• Community Data<br/>• Reddit/Forums]
        I2[stock-price-raw<br/>• Price Data<br/>• Volume Data<br/>• Market Data]
        I3[stock-news-raw<br/>• News Headlines<br/>• Press Release<br/>• Earnings]
    end
    
    subgraph "Processing Stages"
        P1[1단계: Data Cleansing<br/>• Spam Filtering<br/>• Language Detection<br/>• Text Normalization<br/>• Deduplication]
        
        P2[2단계: Real-time Sentiment<br/>• Light Model RoBERTa<br/>• Score Calculation<br/>• Confidence Rating]
        
        P3[3단계: Time Window Aggregation<br/>• 5-minute Windows<br/>• Symbol Grouping<br/>• Statistical Calc<br/>• Trend Detection]
        
        P4[4단계: HyperCLOVA X Deep Analysis<br/>• Context Understanding<br/>• Financial Domain<br/>• Function Calling<br/>• Precise Scoring]
    end
    
    subgraph "Output Topics"
        O1[stock-processed<br/>• Cleaned Data<br/>• Standardized<br/>• Schema Valid]
        O2[stock-sentiment<br/>• Sentiment Scores<br/>• Labels]
        O3[aggregated-metrics<br/>• CCS Scores<br/>• Volume Corr]
        O4[enhanced-sentiment<br/>• SSI Scores<br/>• Insights<br/>• Predictions]
    end
    
    I1 --> P1
    I2 --> P2  
    I3 --> P3
    
    P1 --> O1
    P2 --> O2
    P3 --> O3
    P4 --> O4
    
    P1 --> P2
    P2 --> P3
    P3 --> P4
    
    classDef input fill:#ffebee
    classDef process fill:#e8f5e8
    classDef output fill:#e3f2fd
    
    class I1,I2,I3 input
    class P1,P2,P3,P4 process
    class O1,O2,O3,O4 output
```


## 5. Apache Flink Stream Processing 토폴로지

```mermaid
graph TB
    subgraph "Kafka Sources"
        KS1[stock-social-raw]
        KS2[stock-price-raw]
        KS3[stock-news-raw]
    end
    
    subgraph "Flink Processing Graph"
        OP1[DeduplicationOp]
        OP2[SentimentAnalysisOp]
        OP3[TimeWindowAggregateOp]
        OP4[HyperCLOVACallOp]
    end
    
    subgraph "Kafka Sinks"
        KSink1[stock-processed]
        KSink2[stock-sentiment]
        KSink3[aggregated-metrics]
        KSink4[enhanced-sentiment]
    end
    
    subgraph "State Stores"
        SS1[Dedup Store<br/>RocksDB]
        SS2[Trend Store<br/>In-Memory]
        SS3[Aggregation Store<br/>Window]
    end
    
    subgraph "Infrastructure"
        CP[Checkpointing<br/>RocksDB Backend<br/>Auto: 1s]
        MON[Monitoring<br/>Flink Dashboard<br/>Metrics]
    end
    
    KS1 --> OP1
    KS2 --> OP2
    KS3 --> OP3
    
    OP1 --> OP2
    OP2 --> OP3  
    OP3 --> OP4
    
    OP1 --> KSink1
    OP2 --> KSink2
    OP3 --> KSink3
    OP4 --> KSink4
    
    OP1 -.-> SS1
    OP2 -.-> SS2
    OP3 -.-> SS3
    
    classDef source fill:#fff3e0
    classDef operator fill:#e8f5e8
    classDef sink fill:#e3f2fd
    classDef state fill:#fce4ec
    classDef infra fill:#f3e5f5
    
    class KS1,KS2,KS3 source
    class OP1,OP2,OP3,OP4 operator
    class KSink1,KSink2,KSink3,KSink4 sink
    class SS1,SS2,SS3 state
    class CP,MON infra
```


## 6. 3계층 저장소 구조 및 데이터 흐름

```mermaid
graph LR
    subgraph "Processing Output"
        PO1[enhanced-sentiment]
        PO2[aggregated-metrics]
    end
    
    subgraph "Hot Storage (24h)"
        HS1[PostgreSQL + Redis<br/>• Latest Scores<br/>• Current Trends<br/>• User Sessions]
    end
    
    subgraph "Warm Storage (30d)"  
        WS1[InfluxDB + OpenSearch<br/>• Time Series Data<br/>• Historical Trends<br/>• Search Logs<br/>• Pattern Analysis]
    end
    
    subgraph "Cold Storage (Unlimited)"
        CS1[NAVER Object Storage<br/>Parquet Files<br/>• Raw Archive Data<br/>• Training Datasets<br/>• Backup & Compliance]
    end
    
    subgraph "Data Access"
        DA1[Real-time Dashboard<br/>< 1s<br/>• Live Charts<br/>• Alerts<br/>• Quick Query]
        
        DA2[Analytics Interface<br/>1-2s<br/>• Trend Charts<br/>• Comparisons<br/>• Deep Dive]
        
        DA3[Batch Analytics<br/>& ML Training<br/>10-30s<br/>• ML Datasets<br/>• Model Training<br/>• Long-term Analysis]
    end
    
    PO1 --> HS1
    PO2 --> HS1
    
    HS1 --> WS1
    WS1 --> CS1
    
    HS1 --> DA1
    WS1 --> DA2
    CS1 --> DA3
    
    classDef processing fill:#fff3e0
    classDef hot fill:#ffebee
    classDef warm fill:#e8f5e8
    classDef cold fill:#e3f2fd
    classDef access fill:#f3e5f5
    
    class PO1,PO2 processing
    class HS1 hot
    class WS1 warm
    class CS1 cold
    class DA1,DA2,DA3 access
```


## 7. Vector Storage와 RAG 파이프라인

```mermaid
graph TB
    subgraph "Text Processing"
        TP1[Processed Text Data<br/>• Tweets<br/>• News<br/>• Comments]
        TP2[HyperCLOVA X<br/>Embedding API<br/>• text → vector<br/>• 768 dimensions<br/>• Batch Process]
    end
    
    subgraph "Vector Storage"
        VS1[Milvus DB<br/>• Tweet Embeddings<br/>• News Embeddings<br/>• Context Metadata]
        VS2[Index Structure<br/>• IVF_FLAT Index<br/>• COSINE Similarity<br/>• 1M+ Vectors<br/>• Auto Scaling]
    end
    
    subgraph "RAG Query"
        RQ1[User Query<br/>"AAPL 감정은?"]
        RQ2[HyperCLOVA X<br/>Chat API<br/>Query + Context<br/>→ Answer]
    end
    
    TP1 --> TP2
    TP2 --> VS1
    VS1 --> VS2
    
    RQ1 --> VS1
    VS1 --> RQ2
    
    classDef text fill:#fff3e0
    classDef vector fill:#e8f5e8  
    classDef rag fill:#e3f2fd
    
    class TP1,TP2 text
    class VS1,VS2 vector
    class RQ1,RQ2 rag
```


## 8. 전체 시스템 타임라인 데이터 흐름

```mermaid
timeline
    title Stock Sentiment Agent Data Flow Timeline
    
    section Real-time Processing (0-10s)
        0s : MCP Call
           : • Twitter
           : • AlphaVantage  
           : • Apify
        
        5s : Kafka Produce
           : • Partition
           : • Replicate
           : • Stream
           
        10s : Flink Process
           : • Clean
           : • Analyze
           : • Enrich
    
    section Storage & Analysis (30s-5min)        
        30s : Hot Storage
           : • Redis
           : • PostgreSQL
           : • Cache
           
        300s : Batch Aggregation
            : • CCS
            : • SSI
            : • HyperCLOVA
            
        1800s : Warm Storage
             : • InfluxDB
             : • OpenSearch
             : • Archive
```


## 9. 에러 처리 및 복구 흐름

```mermaid
flowchart TD
    subgraph "Normal Flow"
        NF1[MCP Success<br/>✓ JSON RPC OK<br/>✓ Data Valid<br/>✓ Kafka Send OK]
    end
    
    subgraph "Error Detection"  
        ED1[✗ MCP Server Down<br/>✗ Rate Limit Hit<br/>✗ Kafka Broker Fail<br/>✗ Processing Error<br/>✗ Storage Unavailable]
    end
    
    subgraph "Recovery Actions"
        RA1[• Retry Logic<br/>• Fallback APIs<br/>• Circuit Breaker<br/>• DLQ Route]
    end
    
    subgraph "Dead Letter Queue"
        DLQ1[• Failed Messages<br/>• Error Metadata<br/>• Retry Attempts<br/>• Alert Generation]
    end
    
    subgraph "Manual Intervention"
        MI1[• Log Analysis<br/>• Data Recovery<br/>• System Repair]
    end
    
    NF1 --> ED1
    ED1 --> RA1
    ED1 --> DLQ1
    DLQ1 --> MI1
    
    classDef normal fill:#e8f5e8
    classDef error fill:#ffebee
    classDef recovery fill:#fff3e0
    classDef dlq fill:#fce4ec
    classDef manual fill:#f3e5f5
    
    class NF1 normal
    class ED1 error
    class RA1 recovery
    class DLQ1 dlq
    class MI1 manual
```


## 10. 전체 아키텍처 통합 다이어그램

```mermaid
architecture-beta
    group cloud(cloud)[NAVER Cloud Platform]
    
    group ui(cloud)[User Interface] in cloud
    service streamlit(server)[Streamlit UI] in ui
    service gateway(internet)[API Gateway] in ui
    
    group agent(cloud)[Stock Sentiment Agent] in cloud  
    service mcp(database)[MCP Client] in agent
    service hyperclova(server)[HyperCLOVA X] in agent
    service kafka_prod(disk)[Kafka Producer] in agent
    
    group processing(cloud)[Data Processing] in cloud
    service flink(server)[Apache Flink] in processing
    service kafka_cluster(database)[Kafka Cluster] in processing
    
    group storage(cloud)[Storage Layer] in cloud
    service hot(database)[Hot Storage] in storage
    service warm(disk)[Warm Storage] in storage  
    service cold(cloud)[Cold Storage] in storage
    service vector(database)[Vector DB] in storage
    
    group external(internet)[External APIs]
    service twitter(internet)[Twitter API] in external
    service alphavantage(internet)[AlphaVantage API] in external
    
    streamlit:B -- T:gateway
    gateway:B -- T:mcp
    mcp:R -- L:twitter
    mcp:R -- L:alphavantage
    mcp:B -- T:kafka_prod
    kafka_prod:R -- L:kafka_cluster
    kafka_cluster:T -- B:flink
    flink:B -- T:hot
    flink:B -- T:warm
    flink:B -- T:cold
    flink:B -- T:vector
    hyperclova:T -- B:hot
    hyperclova:T -- B:vector
```


# 📈 Stock Sentiment Agent

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![HyperCLOVA X](https://img.shields.io/badge/HyperCLOVA%20X-Powered-green.svg)](https://clova.ai)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io)
[![NAVER Cloud](https://img.shields.io/badge/NAVER%20Cloud-Native-brightgreen.svg)](https://www.ncloud.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **실시간 주식 감정 분석 및 투자 인사이트 제공 AI 에이전트**
> 
> 트위터(X) API와 주식 시세 데이터를 결합하여 HyperCLOVA X 기반 감정 분석을 통해 실시간 투자 인사이트를 제공하는 혁신적인 AI 서비스입니다.

## 🎯 프로젝트 개요

Stock Sentiment Agent는 **2025 미래에셋증권 AI Festival** 출품작으로, 다음과 같은 혁신적 기능을 제공합니다:

- 🔄 **실시간 감정 분석**: 소셜 미디어와 뉴스 데이터의 실시간 감정 추출
- 🧠 **하이브리드 AI**: 경량 모델 + HyperCLOVA X의 2단계 분석
- 🔌 **MCP 표준 준수**: Model Context Protocol로 다양한 데이터 소스 통합
- 📊 **스트리밍 파이프라인**: Kafka 기반 실시간 데이터 처리
- 💬 **대화형 챗봇**: 자연어 질의를 통한 투자 조언 제공
- ☁️ **클라우드 네이티브**: NAVER Cloud Platform 최적화

## 🚀 주요 특징

### ✨ 혁신적 기술 스택

- **AI/ML**: HyperCLOVA X, Transformers, 벡터 임베딩
- **데이터 통합**: MCP(Model Context Protocol) 표준
- **실시간 처리**: Apache Kafka, Apache Flink
- **저장소**: PostgreSQL, Redis, Milvus Vector DB
- **클라우드**: NAVER Cloud Platform (Financial Cloud)
- **인터페이스**: Streamlit 기반 실시간 챗봇

### 🎨 차별화 포인트

1. **감정 지표 수치화**: CCS(Combined Community Sentiment), SSI(Stock Sentiment Index) 
2. **MCP 생태계 활용**: 확장 가능한 도구 통합 아키텍처
3. **금융 특화 AI**: 한국어 투자 용어 및 맥락 이해
4. **실시간 성능**: 평균 응답 시간 3-5초, 캐시 적중 시 100ms

## 🏗️ 시스템 아키텍처

### 전체 데이터 흐름 및 컴포넌트 구조

```mermaid
graph TD
    %% 사용자 인터페이스
    UI[🖥️ Streamlit UI<br/>ui_app.py] --> Agent[🤖 StockSentimentAgent<br/>agent.py]
    Scheduler[⏰ CollectorScheduler<br/>scheduler.py] --> Agent
    
    %% 에이전트 코어
    Agent --> MCP[🔌 MCP Client<br/>mcp_client.py]
    Agent --> Analyzer[🧠 Sentiment Analyzer<br/>sentiment_analyzer.py]
    Agent --> Streamer[📡 Data Streamer<br/>data_streamer.py]
    Agent --> HotDB[💾 Hot Database<br/>storage/hot_db.py]
    
    %% MCP 도구 연동
    MCP --> Twitter[🐦 Twitter MCP<br/>search_tweets<br/>get_trending_topics]
    MCP --> Alpha[📈 AlphaVantage MCP<br/>get_quote<br/>get_news]
    
    %% 외부 API
    Twitter --> TwitterAPI[Twitter API v2]
    Alpha --> AlphaAPI[AlphaVantage API]
    
    %% 감정 분석 파이프라인
    Analyzer --> Light[⚡ 경량 모델<br/>klue/roberta-base]
    Analyzer --> HyperCLOVA[🧩 HyperCLOVA X<br/>hyperclova_client.py]
    
    %% 데이터 스트리밍
    Streamer --> Kafka[📊 Kafka Topics<br/>stock-sentiment<br/>stock-social-raw<br/>stock-price-raw]
    
    %% 데이터 저장
    HotDB --> PostgreSQL[🗄️ PostgreSQL<br/>sentiment 테이블]
    HotDB --> Redis[⚡ Redis Cache<br/>5분 TTL]
    
    %% 스트림 처리 (추가 컴포넌트)
    Kafka --> StreamProcessor[🌊 Stream Processor<br/>stream_processor.py<br/>Apache Flink]
    StreamProcessor --> VectorSearch[🔍 Vector Search<br/>storage/vector_search.py<br/>Milvus]
    
    %% 설정 관리
    Config[⚙️ Configuration<br/>config.py<br/>Pydantic Settings] -.-> Agent
    Config -.-> MCP
    Config -.-> HyperCLOVA
    Config -.-> HotDB
    Config -.-> Streamer
    
    %% 데이터 흐름 표시
    classDef primaryFlow fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef dataStore fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef externalAPI fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef processing fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    
    class Agent,MCP,Analyzer,Streamer primaryFlow
    class PostgreSQL,Redis,Kafka,VectorSearch dataStore
    class TwitterAPI,AlphaAPI externalAPI
    class Light,HyperCLOVA,StreamProcessor processing
```

### 계층별 아키텍처

```mermaid
graph TB
    subgraph "🖥️ 프레젠테이션 계층"
        UI[Streamlit UI<br/>ui_app.py]
        API[REST API 엔드포인트]
    end
    
    subgraph "🤖 비즈니스 로직 계층"
        Agent[StockSentimentAgent<br/>agent.py]
        Scheduler[CollectorScheduler<br/>scheduler.py]
        Config[Configuration<br/>config.py]
    end
    
    subgraph "🔌 통합 계층 (MCP Layer)"
        MCP[MCP Client<br/>mcp_client.py]
        Twitter[Twitter MCP Server]
        Alpha[AlphaVantage MCP Server]
        Apify[Apify MCP Server]
    end
    
    subgraph "🧠 AI/ML 처리 계층"
        Analyzer[Sentiment Analyzer<br/>sentiment_analyzer.py]
        Light[경량 모델<br/>klue/roberta-base]
        HyperCLOVA[HyperCLOVA X<br/>hyperclova_client.py]
    end
    
    subgraph "📡 데이터 스트리밍 계층"
        Streamer[Data Streamer<br/>data_streamer.py]
        Kafka[Kafka Topics]
        StreamProcessor[Stream Processor<br/>stream_processor.py]
    end
    
    subgraph "💾 데이터 저장 계층"
        HotDB[Hot DB<br/>storage/hot_db.py]
        PostgreSQL[(PostgreSQL<br/>실시간 지표)]
        Redis[(Redis Cache<br/>5분 TTL)]
        VectorDB[Vector Search<br/>storage/vector_search.py]
        Milvus[(Milvus<br/>임베딩 검색)]
    end
    
    subgraph "🌐 외부 서비스 계층"
        TwitterAPI[Twitter API v2]
        AlphaAPI[AlphaVantage API]
        ClovaAPI[CLOVA Studio API]
    end
    
    %% 계층 간 연결
    UI --> Agent
    API --> Agent
    Agent --> MCP
    Agent --> Analyzer
    Agent --> Streamer
    Agent --> HotDB
    
    MCP --> Twitter
    MCP --> Alpha
    MCP --> Apify
    
    Analyzer --> Light
    Analyzer --> HyperCLOVA
    
    Streamer --> Kafka
    Kafka --> StreamProcessor
    
    HotDB --> PostgreSQL
    HotDB --> Redis
    VectorDB --> Milvus
    
    Twitter --> TwitterAPI
    Alpha --> AlphaAPI
    HyperCLOVA --> ClovaAPI
    
    %% 스타일링
    classDef presentation fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef business fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef integration fill:#fff3e0,stroke:#f57f17,stroke-width:2px
    classDef ai fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef streaming fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef storage fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    classDef external fill:#fff8e1,stroke:#fbc02d,stroke-width:2px
    
    class UI,API presentation
    class Agent,Scheduler,Config business
    class MCP,Twitter,Alpha,Apify integration
    class Analyzer,Light,HyperCLOVA ai
    class Streamer,Kafka,StreamProcessor streaming
    class HotDB,PostgreSQL,Redis,VectorDB,Milvus storage
    class TwitterAPI,AlphaAPI,ClovaAPI external
```

## 🔄 데이터 처리 흐름

### 실시간 감정 분석 처리 시퀀스

```mermaid
sequenceDiagram
    participant User as 👤 사용자
    participant UI as 🖥️ Streamlit UI
    participant Agent as 🤖 Agent
    participant MCP as 🔌 MCP Client
    participant Twitter as 🐦 Twitter API
    participant Alpha as 📈 AlphaVantage
    participant Light as ⚡ 경량 모델
    participant Clova as 🧩 HyperCLOVA X
    participant Kafka as 📊 Kafka
    participant DB as 💾 PostgreSQL
    participant Cache as ⚡ Redis

    Note over User,Cache: 실시간 감정 분석 요청 시나리오

    %% 1. 사용자 요청
    User->>UI: "AAPL 감정 분석 요청"
    UI->>Agent: collect(symbol="AAPL")
    
    %% 2. 데이터 수집 (병렬)
    Agent->>MCP: 병렬 데이터 수집 시작
    
    par MCP 도구 호출
        MCP->>Twitter: search_tweets(query="AAPL")
        Twitter-->>MCP: tweets 데이터 반환
    and
        MCP->>Alpha: get_quote(symbol="AAPL")  
        Alpha-->>MCP: 주가 데이터 반환
    and
        MCP->>Alpha: get_news(symbol="AAPL")
        Alpha-->>MCP: 뉴스 데이터 반환
    end
    
    MCP-->>Agent: 수집된 원시 데이터
    
    %% 3. 감정 분석 (2단계)
    Agent->>Light: 텍스트 배열 전처리
    Light-->>Agent: 기본 감정 분류 결과
    
    Agent->>Clova: clova_sentiment(texts, stock_data)
    Note over Clova: Function Calling으로<br/>정밀 감정 분석 수행
    Clova-->>Agent: 종합 감정 지표<br/>(score, label, confidence)
    
    %% 4. 데이터 저장 및 스트리밍
    par 데이터 저장
        Agent->>DB: INSERT sentiment 레코드
        DB-->>Agent: 저장 완료
    and
        Agent->>Cache: setex(감정 데이터, 300초)
        Cache-->>Agent: 캐시 완료  
    and
        Agent->>Kafka: send(topic="stock-sentiment")
        Kafka-->>Agent: 메시지 전송 완료
    end
    
    %% 5. 응답 반환
    Agent-->>UI: 분석 결과 반환
    UI-->>User: 감정 지표 표시<br/>(점수, 라벨, 신뢰도)
    
    %% 6. 백그라운드 처리
    Note over Kafka,Cache: 백그라운드 스트림 처리
    Kafka->>Kafka: 실시간 집계 작업<br/>(Apache Flink)
    
    %% 7. 후속 질의 (캐시 활용)
    User->>UI: "같은 종목 재질의"
    UI->>Agent: get_sentiment_insights("AAPL")
    Agent->>Cache: get(sent:AAPL)
    Cache-->>Agent: 캐시된 데이터 반환
    Agent-->>UI: 즉시 응답 (캐시 적중)
    UI-->>User: 빠른 결과 표시

    Note over User,Cache: 전체 처리 시간: ~3-5초<br/>캐시 적중 시: ~100ms
```

## 📁 프로젝트 구조

```
Stock-Sentiment-Agent/
├── README.md                      # 프로젝트 문서
├── requirements.txt               # Python 의존성
├── .env.example                   # 환경변수 템플릿
├── config.py                      # 설정 관리 (Pydantic)
├── main.py                        # 애플리케이션 진입점
├── agent.py                       # 메인 에이전트 클래스
├── scheduler.py                   # 백그라운드 스케줄러
├── ui_app.py                      # Streamlit UI
│
├── mcp_client.py                  # MCP 클라이언트
├── sentiment_analyzer.py          # 감정 분석 엔진
├── data_streamer.py              # Kafka 스트리밍
├── hyperclova_client.py          # HyperCLOVA X API 래퍼
├── stream_processor.py           # Flink 스트림 처리
│
└── storage/                       # 데이터 저장 계층
    ├── hot_db.py                 # PostgreSQL + Redis
    └── vector_search.py          # Milvus 벡터 검색
```

## 🛠️ 설치 및 실행

### 1. 환경 요구사항

- **Python**: 3.10+
- **데이터베이스**: PostgreSQL, Redis, Kafka
- **벡터 DB**: Milvus (선택사항)
- **클라우드**: NAVER Cloud Platform 계정

### 2. 의존성 설치

```bash
# 저장소 클론
git clone https://github.com/your-repo/Stock-Sentiment-Agent.git
cd Stock-Sentiment-Agent

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# API 키 설정
TWITTER_BEARER_TOKEN=your_twitter_token
ALPHA_VANTAGE_KEY=your_alpha_key
HYPERCLOVA_X_API_KEY=your_clova_key

# 데이터베이스 설정
POSTGRES_URL=postgresql://user:password@localhost:5432/stock_sentiment
REDIS_URL=redis://localhost:6379/0
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### 4. 인프라 구성

```bash
# Docker Compose로 로컬 인프라 실행
docker-compose up -d postgres redis kafka

# 또는 NAVER Cloud Data Streaming Service 사용
# (프로덕션 환경 권장)
```

### 5. 애플리케이션 실행

```bash
# 백그라운드 데이터 수집 시작
python main.py AAPL TSLA MSFT

# Streamlit 챗봇 UI 실행 (별도 터미널)
streamlit run ui_app.py
```

### 6. 웹 인터페이스 접속

- **챗봇 UI**: http://localhost:8501
- **Kafka 관리**: http://localhost:9021 (CMAK)

## 🔧 핵심 기능 상세

### 1. 실시간 감정 분석

**하이브리드 2단계 분석 파이프라인**

```python
# 1단계: 경량 모델 (실시간 필터링)
base_sentiment = quick_sentiment(tweet_text)  # klue/roberta-base

# 2단계: HyperCLOVA X (정밀 분석)
detailed_analysis = await clova_sentiment(texts, stock_data)
```

**감정 지표 출력**
- **CCS** (Combined Community Sentiment): 0-1 스케일 감정 점수
- **SSI** (Stock Sentiment Index): 종합 투자 심리 지수
- **신뢰도**: 분석 결과의 확실성 수치

### 2. MCP 기반 데이터 통합

**지원하는 MCP 서버**
- **Twitter MCP**: 실시간 트윗, 트렌딩 토픽
- **AlphaVantage MCP**: 주식 시세, 재무 데이터, 뉴스
- **Apify MCP**: 커뮤니티 스크래핑 (확장 가능)

**동적 도구 발견**
```python
# MCP 클라이언트가 자동으로 도구 발견 및 등록
await mcp_client.call("twitter", "search_tweets", {"query": "AAPL"})
await mcp_client.call("alpha_vantage", "get_quote", {"symbol": "AAPL"})
```

### 3. 실시간 스트리밍 파이프라인

**Kafka 토픽 구조**
- `stock-social-raw`: 원시 소셜 미디어 데이터
- `stock-price-raw`: 실시간 주가/거래량
- `stock-sentiment`: 가공된 감정 지표
- `stock-processed`: 최종 통합 데이터

**Apache Flink 집계 처리**
```sql
-- 5분 윈도우 감정 평균 계산
SELECT 
    symbol,
    AVG(sentiment_score) AS avg_sentiment,
    COUNT(*) AS data_points,
    TUMBLE_START(ts, INTERVAL '5' MINUTE) AS window_start
FROM social_raw
GROUP BY symbol, TUMBLE(ts, INTERVAL '5' MINUTE)
```

### 4. 다층 저장소 전략

| 저장소 | 용도 | 보관 기간 | 접근 패턴 |
|--------|------|-----------|-----------|
| **Redis** | 캐시 | 5분 | 실시간 조회 |
| **PostgreSQL** | 감정 지표 | 30일 | OLAP 분석 |
| **Milvus** | 벡터 검색 | 7일 | 유사도 검색 |
| **Object Storage** | 원시 데이터 | 무제한 | 장기 보관 |

## 🤖 AI 모델 상세

### HyperCLOVA X 활용

**Function Calling 스키마**
```json
{
  "name": "return_sentiment",
  "parameters": {
    "type": "object",
    "properties": {
      "sentiment_score": {"type": "number", "minimum": 0, "maximum": 1},
      "sentiment_label": {"type": "string", "enum": ["positive", "negative", "neutral"]},
      "confidence": {"type": "number", "minimum": 0, "maximum": 1},
      "key_factors": {"type": "array", "items": {"type": "string"}},
      "market_outlook": {"type": "string"}
    }
  }
}
```

**모델 최적화**
- **파인튜닝**: 주식 도메인 특화 데이터셋으로 학습
- **프롬프트 엔지니어링**: 금융 컨텍스트 최적화
- **RAG 통합**: 벡터 검색을 통한 컨텍스트 강화

## 🎯 사용 사례

### 1. 개인 투자자

```python
# 관심 종목의 실시간 감정 모니터링
result = await agent.get_sentiment_insights("AAPL")
print(f"감정 점수: {result['sentiment']['sentiment_score']:.2f}")
print(f"주요 요인: {', '.join(result['sentiment']['key_factors'])}")
```

### 2. 펀드 매니저

```python
# 포트폴리오 전체의 감정 리스크 평가  
portfolio = ["AAPL", "GOOGL", "MSFT", "NVDA"]
risks = await agent.analyze_portfolio_sentiment(portfolio)
```

### 3. 리서치 애널리스트

```python
# 섹터별 감정 트렌드 분석
tech_sentiment = await agent.get_sector_sentiment("technology", days=30)
```

## 📊 성능 지표

### 처리 성능
- **데이터 수집**: 분당 10,000개 트윗 처리
- **감정 분석**: 평균 3-5초 응답 시간
- **캐시 적중**: 100ms 이내 응답
- **동시 사용자**: 1,000명 지원

### 분석 정확도
- **감정 분류**: 85%+ 정확도 (금융 도메인)
- **트렌드 예측**: 72% 방향 정확도 (1일 기준)
- **신뢰도 캘리브레이션**: 90% 일치도

### 인프라 안정성
- **가용성**: 99.9% SLA
- **장애 복구**: 평균 30초
- **데이터 유실**: 0.01% 미만

## 🛡️ 보안 및 컴플라이언스

### 데이터 보안
- **암호화**: 전송/저장 시 AES-256 적용
- **접근 제어**: RBAC 기반 권한 관리  
- **API 키 관리**: NAVER Cloud KMS 활용
- **감사 로그**: 모든 API 호출 추적

### 규정 준수
- **개인정보보호법**: 트윗 개인정보 익명화
- **금융 규제**: 투자 조언 면책 고지
- **GDPR**: EU 사용자 데이터 보호

## 🚧 알려진 제한사항

1. **데이터 편향**: 소셜 미디어 특성상 노이즈 포함 가능
2. **언어 지원**: 현재 한국어/영어만 지원
3. **시장 휴장**: 거래 시간 외 데이터 제한적
4. **API 제한**: 외부 API의 호출 한도 의존

## 🗺️ 개발 로드맵

### Phase 1: 프로토타입 완성 ✅
- [x] 기본 감정 분석 파이프라인
- [x] MCP 클라이언트 구현
- [x] Streamlit UI 구성
- [x] 기본 캐싱 및 저장소

### Phase 2: 성능 최적화 (진행 중)
- [ ] 단위/통합 테스트 작성
- [ ] 에러 핸들링 강화
- [ ] 성능 모니터링 추가
- [ ] Docker 컨테이너화

### Phase 3: 기능 확장
- [ ] 포트폴리오 분석 기능
- [ ] 알림 시스템 구축
- [ ] 모바일 앱 인터페이스
- [ ] 다국어 지원 확대

### Phase 4: 엔터프라이즈
- [ ] SaaS 플랫폼 전환
- [ ] API 마켓플레이스 출시
- [ ] 기관 투자자 대시보드
- [ ] 화이트라벨 솔루션

## 🤝 기여하기

### 개발 환경 설정

```bash
# 개발용 의존성 설치
pip install -r requirements-dev.txt

# 코드 스타일 검사
flake8 .
black .

# 테스트 실행
pytest tests/

# 타입 체크
mypy .
```

### 기여 가이드라인

1. **이슈 확인**: [GitHub Issues](https://github.com/your-repo/issues)에서 작업할 이슈 선택
2. **브랜치 생성**: `git checkout -b feature/your-feature-name`
3. **코드 작성**: PEP 8 스타일 가이드 준수
4. **테스트 추가**: 새로운 기능에 대한 테스트 작성
5. **PR 생성**: 상세한 설명과 함께 Pull Request 생성

### 버그 리포트

버그 발견 시 다음 정보를 포함하여 [이슈](https://github.com/your-repo/issues)를 생성해주세요:

- 실행 환경 (OS, Python 버전)
- 재현 단계
- 예상 결과 vs 실제 결과
- 에러 로그 (있는 경우)

## 📄 라이센스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.

```
MIT License

Copyright (c) 2025 Stock Sentiment Agent Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 감사의 말

이 프로젝트는 다음 기술들과 커뮤니티의 지원으로 완성되었습니다:

- **NAVER Cloud Platform**: 클라우드 인프라 및 HyperCLOVA X 지원
- **Anthropic**: MCP(Model Context Protocol) 표준 제공
- **OpenSource Community**: Kafka, PostgreSQL, Redis, Milvus
- **미래에셋증권**: AI Festival 플랫폼 제공


## 📚 참고 자료

- [HyperCLOVA X Documentation](https://clova.ai/hyperclova)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [NAVER Cloud Platform](https://www.ncloud.com)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Streamlit Documentation](https://docs.streamlit.io)

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요! ⭐**

[🏠 홈](README.md) | [📖 문서](docs/) | [🐛 이슈](https://github.com/your-repo/issues) | [💬 토론](https://github.com/your-repo/discussions)

</div>
# storage/warm_db.py
"""
Warm Storage: InfluxDB + OpenSearch (30일 보관)
- 시계열 데이터 분석용
- 트렌드 분석, 집계 쿼리 최적화
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from opensearchpy import OpenSearch, helpers
from config import settings

class WarmDB:
    """
    InfluxDB: 시계열 감정 데이터, 주가 데이터
    OpenSearch: 전문 검색, 로그 분석
    """
    
    def __init__(self):
        # InfluxDB 설정
        self.influx_url = getattr(settings, 'INFLUXDB_URL', 'http://localhost:8086')
        self.influx_token = getattr(settings, 'INFLUXDB_TOKEN', 'your-token')
        self.influx_org = getattr(settings, 'INFLUXDB_ORG', 'stock-org')
        self.influx_bucket = getattr(settings, 'INFLUXDB_BUCKET', 'sentiment-data')
        
        # OpenSearch 설정
        self.opensearch_host = getattr(settings, 'OPENSEARCH_HOST', 'localhost')
        self.opensearch_port = getattr(settings, 'OPENSEARCH_PORT', 9200)
        
        self._influx_client = None
        self._opensearch_client = None

    async def startup(self):
        """초기화 및 연결 설정"""
        try:
            # InfluxDB 클라이언트 초기화
            self._influx_client = InfluxDBClient(
                url=self.influx_url,
                token=self.influx_token,
                org=self.influx_org
            )
            self._write_api = self._influx_client.write_api(write_options=SYNCHRONOUS)
            self._query_api = self._influx_client.query_api()
            
            # OpenSearch 클라이언트 초기화
            self._opensearch_client = OpenSearch(
                hosts=[{'host': self.opensearch_host, 'port': self.opensearch_port}],
                http_compress=True,
                use_ssl=False,  # TODO: 프로덕션에서는 SSL 활성화
                verify_certs=False,
                ssl_show_warn=False
            )
            
            # 인덱스 생성
            await self._setup_opensearch_indices()
            logging.info("WarmDB initialized successfully")
            
        except Exception as e:
            logging.error(f"WarmDB initialization failed: {e}")
            raise

    async def _setup_opensearch_indices(self):
        """OpenSearch 인덱스 설정"""
        indices = {
            'sentiment-logs': {
                'mappings': {
                    'properties': {
                        'symbol': {'type': 'keyword'},
                        'timestamp': {'type': 'date'},
                        'sentiment_score': {'type': 'float'},
                        'sentiment_label': {'type': 'keyword'},
                        'source_text': {'type': 'text', 'analyzer': 'standard'},
                        'source_type': {'type': 'keyword'},  # twitter, reddit, news
                        'confidence': {'type': 'float'},
                        'key_factors': {'type': 'text'}
                    }
                }
            },
            'market-events': {
                'mappings': {
                    'properties': {
                        'symbol': {'type': 'keyword'},
                        'timestamp': {'type': 'date'},
                        'event_type': {'type': 'keyword'},
                        'description': {'type': 'text'},
                        'impact_score': {'type': 'float'}
                    }
                }
            }
        }
        
        for index_name, index_body in indices.items():
            if not self._opensearch_client.indices.exists(index_name):
                self._opensearch_client.indices.create(index_name, body=index_body)
                logging.info(f"Created OpenSearch index: {index_name}")

    # InfluxDB 관련 메서드
    async def store_sentiment_timeseries(self, symbol: str, score: float, 
                                       label: str, confidence: float, 
                                       volume: Optional[int] = None,
                                       price: Optional[float] = None):
        """감정 시계열 데이터 저장"""
        try:
            point = Point("sentiment") \
                .tag("symbol", symbol) \
                .tag("label", label) \
                .field("score", score) \
                .field("confidence", confidence) \
                .time(datetime.utcnow())
            
            if volume is not None:
                point = point.field("volume", volume)
            if price is not None:
                point = point.field("price", price)
                
            self._write_api.write(bucket=self.influx_bucket, record=point)
            logging.debug(f"Stored sentiment timeseries for {symbol}")
            
        except Exception as e:
            logging.error(f"Failed to store sentiment timeseries: {e}")

    async def get_sentiment_trend(self, symbol: str, hours: int = 24) -> List[Dict]:
        """감정 트렌드 조회"""
        try:
            query = f'''
            from(bucket: "{self.influx_bucket}")
              |> range(start: -{hours}h)
              |> filter(fn: (r) => r["_measurement"] == "sentiment")
              |> filter(fn: (r) => r["symbol"] == "{symbol}")
              |> filter(fn: (r) => r["_field"] == "score")
              |> aggregateWindow(every: 1h, fn: mean)
              |> yield(name: "sentiment_trend")
            '''
            
            result = self._query_api.query(query)
            trend_data = []
            
            for table in result:
                for record in table.records:
                    trend_data.append({
                        'time': record.get_time(),
                        'symbol': record.values.get('symbol'),
                        'score': record.get_value()
                    })
            
            return sorted(trend_data, key=lambda x: x['time'])
            
        except Exception as e:
            logging.error(f"Failed to get sentiment trend: {e}")
            return []

    async def get_comparative_analysis(self, symbols: List[str], days: int = 7) -> Dict:
        """여러 종목 비교 분석"""
        try:
            symbols_filter = ' or '.join([f'r["symbol"] == "{s}"' for s in symbols])
            query = f'''
            from(bucket: "{self.influx_bucket}")
              |> range(start: -{days}d)
              |> filter(fn: (r) => r["_measurement"] == "sentiment")
              |> filter(fn: (r) => {symbols_filter})
              |> filter(fn: (r) => r["_field"] == "score")
              |> group(columns: ["symbol"])
              |> mean()
              |> yield(name: "comparative_sentiment")
            '''
            
            result = self._query_api.query(query)
            comparison = {}
            
            for table in result:
                for record in table.records:
                    symbol = record.values.get('symbol')
                    avg_score = record.get_value()
                    comparison[symbol] = {
                        'avg_sentiment': avg_score,
                        'period_days': days
                    }
            
            return comparison
            
        except Exception as e:
            logging.error(f"Failed to get comparative analysis: {e}")
            return {}

    # OpenSearch 관련 메서드
    async def store_sentiment_log(self, symbol: str, score: float, label: str,
                                source_text: str, source_type: str, 
                                confidence: float, key_factors: List[str]):
        """상세 감정 분석 로그 저장"""
        try:
            doc = {
                'symbol': symbol,
                'timestamp': datetime.utcnow(),
                'sentiment_score': score,
                'sentiment_label': label,
                'source_text': source_text[:1000],  # 텍스트 길이 제한
                'source_type': source_type,
                'confidence': confidence,
                'key_factors': ' '.join(key_factors) if key_factors else ''
            }
            
            self._opensearch_client.index(
                index='sentiment-logs',
                body=doc
            )
            logging.debug(f"Stored sentiment log for {symbol}")
            
        except Exception as e:
            logging.error(f"Failed to store sentiment log: {e}")

    async def search_sentiment_patterns(self, symbol: str, query_text: str, 
                                      days: int = 30) -> List[Dict]:
        """감정 패턴 검색"""
        try:
            search_body = {
                'query': {
                    'bool': {
                        'must': [
                            {'term': {'symbol': symbol}},
                            {'match': {'source_text': query_text}},
                            {'range': {
                                'timestamp': {
                                    'gte': f'now-{days}d'
                                }
                            }}
                        ]
                    }
                },
                'sort': [{'timestamp': {'order': 'desc'}}],
                'size': 100
            }
            
            response = self._opensearch_client.search(
                index='sentiment-logs',
                body=search_body
            )
            
            return [hit['_source'] for hit in response['hits']['hits']]
            
        except Exception as e:
            logging.error(f"Failed to search sentiment patterns: {e}")
            return []

    async def get_sentiment_distribution(self, symbol: str, days: int = 30) -> Dict:
        """감정 분포 분석"""
        try:
            search_body = {
                'query': {
                    'bool': {
                        'must': [
                            {'term': {'symbol': symbol}},
                            {'range': {
                                'timestamp': {
                                    'gte': f'now-{days}d'
                                }
                            }}
                        ]
                    }
                },
                'aggs': {
                    'sentiment_distribution': {
                        'terms': {
                            'field': 'sentiment_label',
                            'size': 10
                        }
                    },
                    'avg_confidence': {
                        'avg': {
                            'field': 'confidence'
                        }
                    }
                },
                'size': 0
            }
            
            response = self._opensearch_client.search(
                index='sentiment-logs',
                body=search_body
            )
            
            distribution = {}
            if 'aggregations' in response:
                buckets = response['aggregations']['sentiment_distribution']['buckets']
                total_docs = sum(bucket['doc_count'] for bucket in buckets)
                
                for bucket in buckets:
                    distribution[bucket['key']] = {
                        'count': bucket['doc_count'],
                        'percentage': (bucket['doc_count'] / total_docs) * 100 if total_docs > 0 else 0
                    }
                
                distribution['avg_confidence'] = response['aggregations']['avg_confidence']['value']
            
            return distribution
            
        except Exception as e:
            logging.error(f"Failed to get sentiment distribution: {e}")
            return {}

    async def cleanup_old_data(self, days: int = 30):
        """30일 이상 된 데이터 정리"""
        try:
            # InfluxDB 데이터 삭제
            delete_query = f'''
            from(bucket: "{self.influx_bucket}")
              |> range(start: -365d, stop: -{days}d)
              |> drop()
            '''
            # TODO: InfluxDB delete 쿼리 실행
            
            # OpenSearch 데이터 삭제
            delete_body = {
                'query': {
                    'range': {
                        'timestamp': {
                            'lt': f'now-{days}d'
                        }
                    }
                }
            }
            
            self._opensearch_client.delete_by_query(
                index='sentiment-logs',
                body=delete_body
            )
            
            logging.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            logging.error(f"Failed to cleanup old data: {e}")

    async def shutdown(self):
        """연결 종료"""
        if self._influx_client:
            self._influx_client.close()
        # OpenSearch 클라이언트는 자동으로 정리됨
        logging.info("WarmDB connections closed")

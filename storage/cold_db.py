# storage/cold_store.py
"""
Cold Storage: NAVER Cloud Object Storage (무제한 보관)
- Parquet 형식 대용량 데이터 아카이브
- 머신러닝 학습용 데이터셋 관리
- 배치 분석, 데이터 레이크 기능
"""
import logging
import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Iterator
from io import BytesIO
from pathlib import Path
from config import settings

class ColdStorage:
    """
    NAVER Cloud Object Storage를 활용한 장기 보관 스토리지
    S3 호환 API 사용
    """
    
    def __init__(self):
        # NAVER Cloud Object Storage 설정
        self.endpoint_url = getattr(settings, 'NCLOUD_OBJECT_STORAGE_ENDPOINT', 
                                  'https://kr.object.ncloudstorage.com')
        self.access_key = getattr(settings, 'NCLOUD_ACCESS_KEY', 'your-access-key')
        self.secret_key = getattr(settings, 'NCLOUD_SECRET_KEY', 'your-secret-key')
        self.bucket_name = getattr(settings, 'NCLOUD_BUCKET_NAME', 'stock-sentiment-archive')
        
        # S3 호환 클라이언트 초기화
        self._s3_client = None
        
        # 데이터 경로 구조
        self.data_paths = {
            'sentiment': 'sentiment-data/year={year}/month={month}/day={day}/',
            'tweets': 'social-data/tweets/year={year}/month={month}/day={day}/',
            'market': 'market-data/year={year}/month={month}/day={day}/',
            'models': 'ml-models/',
            'datasets': 'training-datasets/'
        }

    async def startup(self):
        """초기화 및 버킷 생성"""
        try:
            self._s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name='kr-standard'  # NAVER Cloud 리전
            )
            
            # 버킷 존재 확인 및 생성
            await self._ensure_bucket_exists()
            logging.info("ColdStorage initialized successfully")
            
        except Exception as e:
            logging.error(f"ColdStorage initialization failed: {e}")
            raise

    async def _ensure_bucket_exists(self):
        """버킷 존재 확인 및 생성"""
        try:
            self._s3_client.head_bucket(Bucket=self.bucket_name)
            logging.info(f"Bucket {self.bucket_name} already exists")
        except:
            try:
                self._s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': 'kr-standard'}
                )
                logging.info(f"Created bucket {self.bucket_name}")
            except Exception as e:
                logging.error(f"Failed to create bucket: {e}")
                raise

    def _get_data_path(self, data_type: str, date: datetime) -> str:
        """날짜 기반 데이터 경로 생성"""
        if data_type not in self.data_paths:
            raise ValueError(f"Unknown data type: {data_type}")
        
        return self.data_paths[data_type].format(
            year=date.year,
            month=f"{date.month:02d}",
            day=f"{date.day:02d}"
        )

    async def archive_sentiment_data(self, data: List[Dict], date: datetime):
        """감정 데이터 Parquet 형식으로 아카이브"""
        try:
            if not data:
                logging.warning("No sentiment data to archive")
                return
            
            # DataFrame 변환
            df = pd.DataFrame(data)
            df['archived_at'] = datetime.utcnow()
            
            # Parquet 파일로 변환
            buffer = BytesIO()
            table = pa.Table.from_pandas(df)
            pq.write_table(table, buffer, compression='snappy')
            buffer.seek(0)
            
            # Object Storage에 업로드
            path = self._get_data_path('sentiment', date)
            filename = f"sentiment_{date.strftime('%Y%m%d')}.parquet"
            key = path + filename
            
            self._s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=buffer.getvalue(),
                ContentType='application/octet-stream',
                Metadata={
                    'data-type': 'sentiment',
                    'record-count': str(len(data)),
                    'compression': 'snappy'
                }
            )
            
            logging.info(f"Archived {len(data)} sentiment records to {key}")
            
        except Exception as e:
            logging.error(f"Failed to archive sentiment data: {e}")

    async def archive_social_data(self, tweets: List[Dict], date: datetime):
        """소셜 미디어 데이터 아카이브"""
        try:
            if not tweets:
                return
            
            # 텍스트 데이터 전처리
            processed_tweets = []
            for tweet in tweets:
                processed_tweets.append({
                    'id': tweet.get('id'),
                    'text': tweet.get('text', '')[:500],  # 텍스트 길이 제한
                    'author': tweet.get('author', ''),
                    'created_at': tweet.get('created_at'),
                    'retweet_count': tweet.get('retweet_count', 0),
                    'like_count': tweet.get('like_count', 0),
                    'symbol': tweet.get('symbol', ''),
                    'source': tweet.get('source', 'twitter'),
                    'archived_at': datetime.utcnow()
                })
            
            df = pd.DataFrame(processed_tweets)
            
            # Parquet으로 압축 저장
            buffer = BytesIO()
            table = pa.Table.from_pandas(df)
            pq.write_table(table, buffer, compression='gzip')
            buffer.seek(0)
            
            path = self._get_data_path('tweets', date)
            filename = f"tweets_{date.strftime('%Y%m%d')}.parquet"
            key = path + filename
            
            self._s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=buffer.getvalue(),
                ContentType='application/octet-stream',
                Metadata={
                    'data-type': 'social-tweets',
                    'record-count': str(len(processed_tweets))
                }
            )
            
            logging.info(f"Archived {len(processed_tweets)} tweets to {key}")
            
        except Exception as e:
            logging.error(f"Failed to archive social data: {e}")

    async def archive_market_data(self, market_data: List[Dict], date: datetime):
        """시장 데이터 아카이브"""
        try:
            if not market_data:
                return
            
            df = pd.DataFrame(market_data)
            df['archived_at'] = datetime.utcnow()
            
            buffer = BytesIO()
            table = pa.Table.from_pandas(df)
            pq.write_table(table, buffer, compression='snappy')
            buffer.seek(0)
            
            path = self._get_data_path('market', date)
            filename = f"market_{date.strftime('%Y%m%d')}.parquet"
            key = path + filename
            
            self._s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=buffer.getvalue(),
                ContentType='application/octet-stream'
            )
            
            logging.info(f"Archived market data to {key}")
            
        except Exception as e:
            logging.error(f"Failed to archive market data: {e}")

    async def load_historical_data(self, data_type: str, start_date: datetime, 
                                 end_date: datetime, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """과거 데이터 로드 (분석용)"""
        try:
            all_data = []
            current_date = start_date
            
            while current_date <= end_date:
                path = self._get_data_path(data_type, current_date)
                
                # 해당 날짜의 파일 목록 조회
                response = self._s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=path
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        # 파일 다운로드 및 로드
                        obj_data = self._s3_client.get_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )
                        
                        buffer = BytesIO(obj_data['Body'].read())
                        df = pd.read_parquet(buffer)
                        
                        # 심볼 필터링
                        if symbols and 'symbol' in df.columns:
                            df = df[df['symbol'].isin(symbols)]
                        
                        all_data.append(df)
                
                current_date += timedelta(days=1)
            
            # 모든 데이터 결합
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                logging.info(f"Loaded {len(combined_df)} records from cold storage")
                return combined_df
            else:
                logging.warning("No data found in specified date range")
                return pd.DataFrame()
                
        except Exception as e:
            logging.error(f"Failed to load historical data: {e}")
            return pd.DataFrame()

    async def create_training_dataset(self, symbols: List[str], 
                                    days_back: int = 90) -> str:
        """머신러닝 학습용 데이터셋 생성"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # 다양한 데이터 소스에서 데이터 수집
            sentiment_data = await self.load_historical_data('sentiment', start_date, end_date, symbols)
            social_data = await self.load_historical_data('tweets', start_date, end_date, symbols)
            market_data = await self.load_historical_data('market', start_date, end_date, symbols)
            
            # 데이터 결합 및 특성 엔지니어링
            dataset = self._prepare_ml_features(sentiment_data, social_data, market_data)
            
            # 학습 데이터셋으로 저장
            dataset_name = f"training_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            key = self.data_paths['datasets'] + dataset_name
            
            buffer = BytesIO()
            table = pa.Table.from_pandas(dataset)
            pq.write_table(table, buffer, compression='snappy')
            buffer.seek(0)
            
            self._s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=buffer.getvalue(),
                ContentType='application/octet-stream',
                Metadata={
                    'data-type': 'training-dataset',
                    'symbols': ','.join(symbols),
                    'days-back': str(days_back),
                    'record-count': str(len(dataset))
                }
            )
            
            logging.info(f"Created training dataset: {key}")
            return key
            
        except Exception as e:
            logging.error(f"Failed to create training dataset: {e}")
            return ""

    def _prepare_ml_features(self, sentiment_df: pd.DataFrame, 
                           social_df: pd.DataFrame, 
                           market_df: pd.DataFrame) -> pd.DataFrame:
        """머신러닝용 특성 준비"""
        try:
            # 간단한 특성 엔지니어링 예시
            features = []
            
            # 감정 데이터 특성
            if not sentiment_df.empty:
                sentiment_features = sentiment_df.groupby(['symbol', 'date']).agg({
                    'sentiment_score': ['mean', 'std'],
                    'confidence': 'mean'
                }).reset_index()
                features.append(sentiment_features)
            
            # 소셜 데이터 특성 (볼륨, 참여도)
            if not social_df.empty:
                social_features = social_df.groupby(['symbol', 'date']).agg({
                    'retweet_count': 'sum',
                    'like_count': 'sum',
                    'id': 'count'  # 트윗 수
                }).reset_index()
                features.append(social_features)
            
            # 시장 데이터와 결합
            if features and not market_df.empty:
                combined = features[0]
                for feature_df in features[1:]:
                    combined = pd.merge(combined, feature_df, on=['symbol', 'date'], how='outer')
                
                final_dataset = pd.merge(combined, market_df, on=['symbol', 'date'], how='left')
                return final_dataset.fillna(0)
            
            return pd.DataFrame()
            
        except Exception as e:
            logging.error(f"Failed to prepare ML features: {e}")
            return pd.DataFrame()

    async def list_archived_data(self, data_type: str, days_back: int = 30) -> List[Dict]:
        """아카이브된 데이터 목록 조회"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            archived_files = []
            current_date = start_date
            
            while current_date <= end_date:
                path = self._get_data_path(data_type, current_date)
                
                response = self._s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=path
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        archived_files.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'],
                            'date': current_date.strftime('%Y-%m-%d')
                        })
                
                current_date += timedelta(days=1)
            
            return archived_files
            
        except Exception as e:
            logging.error(f"Failed to list archived data: {e}")
            return []

    async def cleanup_old_archives(self, days_to_keep: int = 365):
        """오래된 아카이브 정리 (1년 이상)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # 전체 오브젝트 목록 조회
            response = self._s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            deleted_count = 0
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        self._s3_client.delete_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )
                        deleted_count += 1
            
            logging.info(f"Cleaned up {deleted_count} old archive files")
            
        except Exception as e:
            logging.error(f"Failed to cleanup old archives: {e}")

    async def get_storage_stats(self) -> Dict:
        """스토리지 사용량 통계"""
        try:
            response = self._s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            stats = {
                'total_objects': 0,
                'total_size_bytes': 0,
                'data_types': {},
                'oldest_file': None,
                'newest_file': None
            }
            
            if 'Contents' in response:
                dates = []
                for obj in response['Contents']:
                    stats['total_objects'] += 1
                    stats['total_size_bytes'] += obj['Size']
                    dates.append(obj['LastModified'])
                    
                    # 데이터 타입별 분류
                    key_parts = obj['Key'].split('/')
                    if key_parts:
                        data_type = key_parts[0]
                        if data_type not in stats['data_types']:
                            stats['data_types'][data_type] = {'count': 0, 'size': 0}
                        stats['data_types'][data_type]['count'] += 1
                        stats['data_types'][data_type]['size'] += obj['Size']
                
                if dates:
                    stats['oldest_file'] = min(dates)
                    stats['newest_file'] = max(dates)
            
            # 크기를 MB로 변환
            stats['total_size_mb'] = stats['total_size_bytes'] / (1024 * 1024)
            
            return stats
            
        except Exception as e:
            logging.error(f"Failed to get storage stats: {e}")
            return {}

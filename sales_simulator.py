import asyncio
import random
import httpx
from datetime import datetime
from typing import List, Dict, Optional
import time
import os
import glob


class SalesSimulator:
    def __init__(self, backend_url: str = "http://127.0.0.1:8000", interval_seconds: int = 60, # 평소에는 600으로로
                 simulation_mode: bool = True, dummy_csv_file: Optional[str] = None):
        self.backend_url = backend_url
        self.interval_seconds = interval_seconds
        self.simulation_mode = simulation_mode
        self.dummy_csv_file = dummy_csv_file
        self.menus = []  # 메뉴 리스트는 백엔드에서 가져옴
        
    async def fetch_menus(self) -> List[str]:
        """백엔드에서 메뉴 리스트 가져오기"""
        # localhost와 127.0.0.1 둘 다 시도
        urls_to_try = [
            self.backend_url,
            self.backend_url.replace("localhost", "127.0.0.1"),
            self.backend_url.replace("127.0.0.1", "localhost")
        ]
        # 중복 제거
        urls_to_try = list(dict.fromkeys(urls_to_try))
        
        # 엔드포인트 URL (슬래시 포함/미포함 둘 다 시도)
        endpoints = ["/api/v1/menus", "/api/v1/menus/"]
        
        for url in urls_to_try:
            for endpoint in endpoints:
                try:
                    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                        response = await client.get(f"{url}{endpoint}")
                        if response.status_code == 200:
                            menus_data = response.json()
                            # 성공한 URL로 업데이트
                            if url != self.backend_url:
                                self.backend_url = url
                            return [menu["name"] for menu in menus_data]
                        elif response.status_code == 307:
                            # 리다이렉트 발생 - 다음 엔드포인트 시도
                            continue
                        else:
                            print(f"⚠️  메뉴 조회 실패: HTTP {response.status_code} ({url}{endpoint})")
                except httpx.ConnectError:
                    continue  # 다음 URL 시도
                except httpx.TimeoutException:
                    print(f"⏱️  백엔드 서버 응답 시간 초과: {url}{endpoint}")
                    continue
                except Exception as e:
                    print(f"❌ 메뉴 가져오기 실패 ({url}{endpoint}): {e}")
                    continue
        
        # 모든 URL 시도 실패
        print(f"❌ 백엔드 서버에 연결할 수 없습니다. 시도한 URL: {urls_to_try}")
        print("   백엔드 서버가 실행 중인지 확인하세요: uvicorn app.main:app --reload")
        return []
    
    def generate_sales(self, menus: List[str]) -> List[Dict]:
        """랜덤 매출 데이터 생성"""
        sales = []
        if not menus:
            return sales
        
        # 0~3개의 메뉴가 팔림 (랜덤)
        num_sales = random.randint(0, 3)
        selected_menus = random.sample(menus, min(num_sales, len(menus)))
        
        for menu_name in selected_menus:
            quantity = random.randint(1, 5)  # 1~5개 팔림
            sales.append({
                "menu_name": menu_name,
                "quantity": quantity,
                "timestamp": datetime.now().isoformat()
            })
        
        return sales
    
    async def send_sales_to_backend(self, sales: List[Dict]):
        """매출 데이터를 백엔드로 전송"""
        if not sales:
            return
        
        try:
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/sales/receive",
                    json={"sales": sales}
                )
                if response.status_code == 200:
                    print(f"✅ 매출 전송 성공: {len(sales)}건")
                else:
                    print(f"❌ 매출 전송 실패: HTTP {response.status_code}")
        except httpx.ConnectError:
            print(f"❌ 백엔드 서버에 연결할 수 없습니다: {self.backend_url}")
        except httpx.TimeoutException:
            print(f"⏱️  백엔드 서버 응답 시간 초과")
        except Exception as e:
            print(f"❌ 매출 전송 오류: {e}")
    
    async def check_backend_connection(self) -> bool:
        """백엔드 서버 연결 확인"""
        try:
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                response = await client.get(f"{self.backend_url}/health")
                return response.status_code == 200
        except:
            return False
    
    def get_dummy_csv_files(self) -> List[str]:
        """dummy_data 폴더에서 CSV 파일 목록 가져오기"""
        dummy_dir = os.path.join(os.path.dirname(__file__), "dummy_data")
        if not os.path.exists(dummy_dir):
            return []
        
        csv_files = glob.glob(os.path.join(dummy_dir, "*.csv"))
        return [os.path.basename(f) for f in csv_files]
    
    async def load_dummy_csv(self, csv_filename: Optional[str] = None) -> bool:
        """dummy_data 폴더의 CSV 파일을 백엔드에 업로드"""
        dummy_dir = os.path.join(os.path.dirname(__file__), "dummy_data")
        
        # CSV 파일 선택
        if csv_filename:
            csv_path = os.path.join(dummy_dir, csv_filename)
            if not os.path.exists(csv_path):
                print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_filename}")
                return False
        else:
            # 랜덤으로 선택
            csv_files = glob.glob(os.path.join(dummy_dir, "*.csv"))
            if not csv_files:
                print("❌ dummy_data 폴더에 CSV 파일이 없습니다.")
                return False
            csv_path = random.choice(csv_files)
            csv_filename = os.path.basename(csv_path)
        
        print(f"📄 CSV 파일 로드: {csv_filename}")
        
        try:
            # CSV 파일 읽기
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            # 백엔드에 업로드
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                files = {"file": (csv_filename, csv_content.encode('utf-8'), "text/csv")}
                response = await client.post(
                    f"{self.backend_url}/api/v1/menus/upload-csv",
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    menu_count = result.get("message", "").split("개")[0].split()[-1]
                    print(f"✅ {menu_count}개 메뉴가 등록되었습니다.")
                    return True
                else:
                    print(f"❌ CSV 업로드 실패: HTTP {response.status_code}")
                    print(f"   응답: {response.text}")
                    return False
        except Exception as e:
            print(f"❌ CSV 파일 로드 오류: {e}")
            return False
    
    async def run(self):
        """시뮬레이터 실행"""
        print("🔄 가상 매출 시뮬레이터 시작...")
        print(f"⏰ {self.interval_seconds}초마다 매출 데이터 생성")
        print(f"🔗 백엔드 서버: {self.backend_url}")
        print()
        
        # 초기 연결 확인
        print("🔍 백엔드 서버 연결 확인 중...")
        if not await self.check_backend_connection():
            print(f"❌ 백엔드 서버에 연결할 수 없습니다: {self.backend_url}")
            print("   다음 명령어로 백엔드 서버를 먼저 실행하세요:")
            print("   cd back")
            print("   uvicorn app.main:app --reload")
            print()
            print("   서버가 실행되면 시뮬레이터를 다시 시작하세요.")
            return
        print("✅ 백엔드 서버 연결 성공!")
        print()
        
        # 시뮬레이션 모드일 때 dummy CSV 자동 로드
        if self.simulation_mode:
            print("🎮 시뮬레이션 모드: dummy_data에서 CSV 파일 자동 로드")
            csv_files = self.get_dummy_csv_files()
            if csv_files:
                if self.dummy_csv_file and self.dummy_csv_file in csv_files:
                    selected_file = self.dummy_csv_file
                else:
                    selected_file = random.choice(csv_files)
                print(f"📂 사용 가능한 CSV 파일: {', '.join(csv_files)}")
                print(f"🎲 선택된 파일: {selected_file}")
                await self.load_dummy_csv(selected_file)
            else:
                print("⚠️  dummy_data 폴더에 CSV 파일이 없습니다.")
                print("   수동으로 CSV 파일을 업로드하세요: POST /api/v1/menus/upload-csv")
            print()
        
        while True:
            try:
                # 메뉴 리스트 업데이트
                menus = await self.fetch_menus()
                if menus:
                    self.menus = menus
                    print(f"📋 메뉴 {len(menus)}개 로드됨")
                elif not self.menus:
                    print("⚠️  등록된 메뉴가 없습니다. CSV 파일을 먼저 업로드하세요.")
                    print("   API: POST /api/v1/menus/upload-csv")
                
                # 매출 생성 및 전송
                if self.menus:
                    sales = self.generate_sales(self.menus)
                    if sales:
                        print(f"💰 생성된 매출: {sales}")
                        await self.send_sales_to_backend(sales)
                    else:
                        print("⏸️  이번 주기는 매출 없음")
                
                print(f"⏳ {self.interval_seconds}초 대기 중...")
                await asyncio.sleep(self.interval_seconds)
            except KeyboardInterrupt:
                print("\n🛑 시뮬레이터 종료")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                await asyncio.sleep(self.interval_seconds)


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="가상 매출 시뮬레이터")
    parser.add_argument("--url", default=None, help="백엔드 서버 URL")
    parser.add_argument("--interval", type=int, default=60, help="매출 생성 주기 (초)")
    parser.add_argument("--no-simulation", action="store_true", help="시뮬레이션 모드 비활성화 (사용자가 직접 CSV 업로드)")
    parser.add_argument("--csv", default=None, help="사용할 dummy CSV 파일명 (시뮬레이션 모드일 때)")
    
    args = parser.parse_args()
    
    # Windows에서는 127.0.0.1이 더 안정적일 수 있음
    if args.url:
        backend_url = args.url
    elif sys.platform == "win32":
        backend_url = "http://127.0.0.1:8000"
    else:
        backend_url = "http://localhost:8000"
    
    simulation_mode = not args.no_simulation
    
    simulator = SalesSimulator(
        backend_url=backend_url,
        interval_seconds=args.interval,
        simulation_mode=simulation_mode,
        dummy_csv_file=args.csv
    )
    asyncio.run(simulator.run())


# 7Peaks Reads

[7Peaks Reads](https://sevenpeaksone.github.io/reads/)에서 발행하는 뉴스·해설·블로그 기사 저장소입니다.

영문 원본: [README.md](README.md).

사이트와 기사는 아이보리·차콜·라임·주황·보라·녹색의 **light-v5** 디자인을 사용합니다. 메인, 뉴스, 블로그, 분류별 보관함, 즐겨찾기, 기존 기사에 같은 공통 디자인을 적용합니다.

Reads는 회사 홈페이지의 라이트 디자인을 따릅니다. 승인된 A 심볼 로고, 얇은 Geist/Noto Sans KR 서체, 넓은 여백, 라임 탐색 표시, 작은 차콜 버튼, 배경에 자연스럽게 이어지는 홈 사진을 공유합니다. 별도의 잡지 테마를 만들지 않고 이 디자인 체계를 기사 읽기에 맞게 적용합니다.

홈, 모든 목록, 즐겨찾기, 기사 상세는 라이트 모드만 사용합니다. 다크모드 버튼은 제거했습니다. 이전 다크 설정만 정리하고 즐겨찾기·보기 설정은 변경하지 않습니다.

- 공개용 디자인: [`assets/reads-theme.css`](assets/reads-theme.css).
- 수정할 디자인 원본: [`tools/reads-theme/reads_theme.css`](tools/reads-theme/reads_theme.css).
- 생성기·단독 기사 템플릿·검사: [디자인 가이드](tools/reads-theme/README.ko.md).

예전 CSS 위에 스타일을 계속 덧붙이지 말고 원본을 수정한 뒤 HTML을 재생성합니다. 앞으로 생성할 기사에도 디자인이 유지되도록 제작 프로젝트의 템플릿·스타일 사본도 일치시킵니다. 기사 HTML을 만들거나 수정하기 전에 디자인 가이드를 읽습니다.

기존 기사 경로, 이미지, 분류, 보관함, 검색 ID, 즐겨찾기, 발행 방식을 유지합니다. GitHub Pages를 계속 사용하며 기사 파일을 Cloudflare로 이전하지 않습니다.

# 7Peaks Reads 디자인 — lime-v1

한국어 번역입니다. 영문 원본: [README.md](README.md).

기존 [Reads 사이트](https://sevenpeaksone.github.io/reads/)의 확정된 디자인 원본입니다. GitHub Pages 호스팅, 기사 주소, 누적 보관함, 분류, 검색 데이터, 즐겨찾기, 일일 발행 규약을 유지합니다. 기사 파일을 Cloudflare Pages나 R2로 이전하지 않습니다.

## 디자인 원본

- `reads_theme.css`: 아이보리 `#F6F8ED`, 차콜 `#17201B`, 라임 `#D5F43B`, 주황 `#F28B3C`, 보라 `#9270D8`, 녹색 `#2BA978`.
- `assets/7peaks-wordmark-light.svg`: 확정된 로고. 다시 그리거나 앞에 7을 하나 더 붙이지 않습니다.
- `reads_article_template.html`: 단독 미리보기용 기사 문서 구조.
- `render_reads_article.py`: 템플릿·스타일·인라인 로고를 사용해 일관되게 조립하는 도구.
- `rebuild_index.py`: 공통 목록·본문 생성기. 사이트에 공통 로고와 `assets/reads-theme.css`도 설치합니다.
- `test_reads_theme.py`: 단독 조립 및 신규 기사 발행 검사.
- `verify_reads_theme.py`: 원본과 디자인 적용본의 본문·이미지 참조·링크·검색 데이터를 읽기 전용으로 비교하는 검사.

Reads 저장소에서는 `tools/reads-theme/`에 있습니다. 기사 제작 프로젝트에서는 같은 리소스가 `docs/`에 있고, 이 가이드의 파일명은 `docs/READS_DESIGN.md` 및 한국어 번역 `docs/READS_DESIGN.ko.md`입니다.

## 앞으로 생성할 기사 조립

기사마다 임의 CSS를 만들지 않습니다. 기존 흐름으로 초안 Markdown을 본문 HTML 조각으로 변환합니다. 문서 태그와 첫 기사 제목 h1은 제외하고 제목을 별도 인수로 전달합니다. 본문, 출처 링크, 날짜, `./images/...` 경로를 보존합니다.

제작 프로젝트에서 실행합니다.

```sh
python3 docs/render_reads_article.py \
  --title "기사 제목" --category "IT" --date "2026-11-10" \
  --body output/topic/body.html --output output/topic/final.html
```

예시 값이 아니라 실제 메타데이터를 사용합니다. 기존 출력은 기본적으로 덮어쓰지 않습니다. 확인·백업한 뒤 필요한 경우에만 `--overwrite`를 추가합니다. 메타데이터를 이스케이프하고 정확한 스타일·로고를 문서에 포함하므로 로컬 미리보기에 외부 스타일시트가 필요하지 않습니다. 내용 검토용 `final.md`도 유지합니다.

최종 문서는 h1 하나, `body[data-reads-view="article"]`, `data-reads-theme="lime-v1"`를 사용합니다. 미치환 템플릿 토큰을 남기지 않습니다. 해시태그는 두 번째 h1이 아니라 문단으로 표시합니다. 이미지 내용·상대경로, 의미 있는 대체텍스트, 반응형 크기를 유지합니다. 스타일 때문에 리서치, 편집 원칙, 이미지 제작, 주제를 바꾸지 않습니다. 회사 소개에 미구현 AI·위키 기능을 추가하지 않습니다. AI를 주제로 한 뉴스를 금지하는 뜻은 아닙니다.

## 발행 규약

기존 대기함/READY 방식과 일정을 유지합니다. 제작 측 `site.tgz`에는 **`posts/` 또는 `news/` 아래 기사 폴더와 이미지만** 넣습니다. 최상위 `assets/`나 `tools/`는 추가하지 않습니다. 수신 측 생성기가 공통 에셋을 설치하고, 미리보기용 CSS·탐색을 공통 틀 하나로 바꾸며, 예전 인라인 스타일로 들어온 기사에도 확정된 디자인을 적용합니다.

예정된 모든 기사와 참조 파일을 확인한 뒤 마지막에 READY를 작성합니다. 빈 기사나 부분 완성 묶음을 완료로 표시하지 않습니다. 스타일 적용을 이유로 직접 Git 푸시, 인증·일정·이력 파일 수정, 발행 스크립트 변경을 하지 않습니다. 과거 누락 본문·이미지는 별도 보고하며 임의 작성·삭제·복구하지 않습니다.

## 검사

Reads 저장소 루트에서 실행합니다.

```sh
python3 -B -m unittest discover -s tools/reads-theme -p 'test_reads_theme.py' -v
```

대량 생성은 내장 디스크 사본에서 `SITE`에 대상 디렉터리를 명시하고 진행하며 외장 SSD에서는 실행하지 않습니다. 뉴스·블로그 각 한 편의 PC·모바일 화면, 이미지 참조, 검색, 즐겨찾기, 페이지 이동, 본문 밝은/어두운 모드를 확인합니다. 미리보기, 원본 설치, 커밋·푸시, 실제 배포 확인은 구분해서 보고합니다.

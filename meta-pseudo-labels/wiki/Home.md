본 wiki는 Auto-labeling project의 정리글로, 최종 결과물에 대한 내용만을 다루고 있다.

# Auto-labeling Project

## Purpose

일반적인 딥러닝 모델을 supervised learning model로 training data를 위한 labeling을 필요로 한다. 하지만 사람이 직접 labeling을 다 진행하기에는 너무 많은 시간과 돈이 쓰인다. 고로 적은 양의 labeling을 통해 model을 training 시키고자 머신러닝 방법론 중 하나인 semi-supervised learning을 사용하고자 했다.

- [What is Semi-supervised learning?](Semi Supervised Learning)

## Meta Pseudo Labels

여러 semi-supervised learning 알고리즘 중 meta pseudo labels를 이용하여 model을 만들고자 한다.

- [What is Meta Pseudo Labels?](Meta Pseudo Labels 논문 리뷰)

Meta Pseudo Labels 알고리즘을 pytorch로 구현한 git에 있는 코드를 분석하고 조금 수정하여 플랫폼에 탑재했다.

- [MPL 코드 분석](MPL 코드 분석)
- [T3Q MPL 코드](T3Q MPL 코드)
- [T3Q MPL 사용자 가이드](사용자 가이드)
- [Issue](Issue)

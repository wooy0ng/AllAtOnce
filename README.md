<div align="center">
 <h1> AllAtOnce: 강의록 질문 생성 </h1>

 <table>
    <tr>
      <td align="center">메인</td>
      <td align="center">STT</td>
    </tr>
    <tr>
      <td align="center">
        <img width="500px" alt="메인" src="https://github.com/wooy0ng/wooy0ng/assets/37149278/50ee7960-e05e-43ef-b8e7-5ee78b77e680">
      </td>
      <td align="center">
        <img width="500px" alt="STT" src="https://github.com/wooy0ng/wooy0ng/assets/37149278/d0d46fa9-8202-4ecf-ba5a-517acc5f3a40">
      </td>
    </tr>
    <tr>
      <td align="center">요약</td>
      <td align="center">질문 생성</td>
    </tr>
    <tr>
      <td align="center">
        <img width="500px" alt="요약" src="https://github.com/wooy0ng/wooy0ng/assets/37149278/f833430b-cdd8-457f-a31e-957edd21b362">
      </td>
      <td align="center">
        <img width="500px" alt="질문 생성" src="https://github.com/wooy0ng/wooy0ng/assets/37149278/a58a7841-7563-4df9-aa0e-d744e2dc7114">
      </td>
    </tr>
    
 </table>

 <br>
 대면 수업 확대로 기존 녹화 강의에서 실시간 대면 강의로 변화함에 따라 학습에 어려움을 겪는 학생들이 많아졌습니다.  <br />
 이런 불편함을 해소하고자 강의 녹음본을 활용하여 요약본과 예상 질문 및 답안을 생성하여 <br>
 학생들의 효율적인 학습을 돕는 어플리케이션을 제작해보는 프로젝트입니다.<br />
 <br>
 강의 수강 시, 주요 내용을 놓쳐 강의 녹음본을 통해 복습하고자 하는 학생 <br>
 대면 강의 시, 필기 중 주요 내용에 대한 체계적인 정리가 어려운 학생 <br>
 시험 전, 예상 질문과 답안을 통해 공부를 하고자 하는 학생을 대상으로 프로젝트를 진행하였습니다. 
<br>
</div>

<br><br><br>

## ✓ 활용 장비 및 환경
- GPU : NVIDIA A100  
- OS : Ubuntu 18.04 LTS

<br><br>

## ✓ 선정 모델 구조

<b>(1) STT & Post Processing</b>

- 가장 빠르고 CER 평가 지표가 높았던 Whisper 모델을 사용했습니다.
<img src="https://github.com/wooy0ng/wooy0ng/assets/37149278/47000a4c-13cc-4549-b572-bed73c5bf008" width="700px">
<img src="https://github.com/wooy0ng/wooy0ng/assets/37149278/cb0df435-f19a-433e-a96c-88183905984b" width="700px">

<br><br>

- 불완전한 문장은 KoGPT2 모델로 PostProcessing 합니다.
<img src="https://github.com/wooy0ng/wooy0ng/assets/37149278/f7719b61-9e45-4926-ac5a-1b8415c6b266" width="700px">

<br><br>

<b>(2) Summarization</b>

- KoBART를 사용하여 STT과정을 통해 얻은 구문을 요약합니다.
<img src="https://github.com/wooy0ng/wooy0ng/assets/37149278/2cba4739-8586-4d66-95f8-33dae5b6735e" width="700px">

<br><br>

<b>(3) Answer Extraction & Question Generation</b>

<b>Answer Extraction</b>
- KeyBERT와 NER를 활용하여 핵심 키워드를 추출합니다.
- 요약본과 핵심 키워드 간의 코사인 유사도를 이용하여 Ranking을 수행합니다.
<img src="https://github.com/wooy0ng/wooy0ng/assets/37149278/302bb1b9-7922-40d0-adfa-0aafa3ffb1ef" width="700px">

<br><br>

<b>Question Generation</b>
- 요약본(context)와 핵심 키워드를 사용해 질문(Question)을 생성합니다.
<img src="https://github.com/wooy0ng/wooy0ng/assets/37149278/2da2a112-13ee-4c75-81d5-b0a720186fe7" width="700px">

<br><br><br><br>

## ✓ 서비스 아키텍처

<img width="800" alt="main" src="https://github.com/wooy0ng/wooy0ng/assets/37149278/d342c518-cf35-4a45-b006-bcb803504041">


<br><br><br>

## ✓ 사용 기술 스택

<img width="600" alt="main" src="https://github.com/wooy0ng/wooy0ng/assets/37149278/c72694bb-16e5-48ec-afe6-483f69c913a5">





<br><br><br>


## ✓ 팀원 소개
|강혜빈|권현정|백인진|이용우|이준원|
|:--:|:--:|:--:|:--:|:--:|
|<img width="100" alt="에브리타임" src="https://user-images.githubusercontent.com/37149278/216918705-56e2f4d6-bc4f-482a-b9fd-190ca865d0e5.png">|<img width="100" alt="에브리타임" src="https://user-images.githubusercontent.com/37149278/216918785-3bc90fc4-e4b8-43f4-bd61-d797cf87e344.png">|<img width="100" alt="에브리타임" src="https://user-images.githubusercontent.com/37149278/216919234-e9cc433c-f464-4a4b-8601-cffa668b22b2.png">|<img width="100" alt="에브리타임" src="https://user-images.githubusercontent.com/37149278/216919814-f6ff7c2f-90ea-489c-b19a-a29fca8f9861.png">|<img width="100" alt="에브리타임" src="https://user-images.githubusercontent.com/37149278/216919925-1ab02487-e7a5-4995-8d22-1253bbcae550.png">|
|Question Generation|Answer Extraction|Summarization,<br> BE|STT, <br>FE|STT, <br>STT PostProcessing|



<br><br><br>

자세한 정보 및 인사이트는 <a href="https://blog.naver.com/wooy0ng/223018461440">블로그</a>를 참고해주세요! 

<a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fwooy0ng%2Fhit-counter&count_bg=%23ADC83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false"/></a>
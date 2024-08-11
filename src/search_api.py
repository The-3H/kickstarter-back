from search_bot import SearchQA
import re
import pandas as pd
import io
from typing import Union
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SearchInput(BaseModel):
    age: int
    pregnancy_week: int
    input: str

@router.post("/")
async def search(search_input: SearchInput):
    search_qa = SearchQA()
    input = {
        'age' : search_input.age,
        'pregnancy_week': search_input.pregnancy_week,
        'input': search_input.input
    }

    response = search_qa.get_result(input['age'], input['pregnancy_week'], input['input'])

    def extract_safety_level(response):
        match = re.search(r'Safety level:\s*(\d+)', response)
        
        if match:
            # 찾은 숫자를 정수로 변환하여 반환합니다.
            return int(match.group(1))
        else:
            # 안전 수준을 찾지 못한 경우 None을 반환합니다.
            return None

    def parse_by_section(text):
        # 섹션을 분리하는 정규표현식을 더 유연하게 수정
        section_pattern = r'(\d+\.?\s*[^:\n]+):\s*([\s\S]+?)(?=\n(?:\d+\.?\s|$))'
        sections = re.findall(section_pattern, text, re.MULTILINE)
        
        result = {}
        for title, content in sections:
            # 키 생성: 번호 제거, 소문자 변환, 공백을 언더스코어로 변경
            key = re.sub(r'^\d+\.?\s*', '', title).strip().lower().replace(' ', '_')
            # 내용에서 앞뒤 공백 제거
            value = content.strip()
            result[key] = value
        
        return result

    def extract_key_nutrients_section(text):
        pattern = r'2\.\s*Key nutrients and calories calculation\s*([\s\S]+?)(?=\n\d+\.\s|\Z)'
        match = re.search(pattern, text)
        
        if match:
            content = match.group(1).strip()
            return content
        else:
            return None

    def markdown_table_to_dataframe(markdown_table):
        # Markdown 표를 문자열 IO로 변환
        table_io = io.StringIO(markdown_table)
        
        # pandas로 읽기
        df = pd.read_csv(table_io, sep='|', skipinitialspace=True)
        
        # 첫 번째와 마지막 열(비어있는 열) 제거
        df = df.iloc[:, 1:-1]
        
        # 열 이름 정리
        df.columns = df.columns.str.strip()
        
        # 첫 번째 행(구분선) 제거
        df = df.iloc[1:]
        
        # 인덱스 재설정
        df = df.reset_index(drop=True)
        
        return df

    safety_level = extract_safety_level(response=response.raw) #! connect to API
    parsed_data = parse_by_section(response.raw) #! connect to API
    nutrient_table = markdown_table_to_dataframe(extract_key_nutrients_section(response.raw)) #! connect to API

    return {
        "age": input['age'],
        "pregnancy_week": input['pregnancy_week'],
        "input": input['input'],
        "safety_level": safety_level,
        "parsed_data": parsed_data,
        "nutrient_table": nutrient_table
    }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=58000)
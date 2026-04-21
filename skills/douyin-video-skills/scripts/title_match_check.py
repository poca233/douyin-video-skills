#!/usr/bin/env python3
import argparse
import json
import re
import sys


def normalize_title(text: str) -> str:
    text = text.strip()
    text = re.sub(r'[#＃].*$', '', text)  # drop trailing hashtags
    text = re.sub(r'\s+', '', text)
    text = text.replace('“', '"').replace('”', '"').replace('：', ':').replace('。', '')
    return text.lower()


def main():
    parser = argparse.ArgumentParser(description='校验当前弹层标题是否与目标搜索结果标题一致')
    parser.add_argument('--expected', required=True, help='目标搜索结果标题')
    parser.add_argument('--actual', required=True, help='当前弹层标题')
    args = parser.parse_args()

    expected_n = normalize_title(args.expected)
    actual_n = normalize_title(args.actual)
    matched = expected_n == actual_n or expected_n in actual_n or actual_n in expected_n

    result = {
        'matched': matched,
        'expected': args.expected,
        'actual': args.actual,
        'expected_normalized': expected_n,
        'actual_normalized': actual_n,
        'reason': 'title-match' if matched else 'title-mismatch'
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not matched:
        sys.exit(2)


if __name__ == '__main__':
    main()

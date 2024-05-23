import json
import os

import fire
from loguru import logger
from yaml import safe_load

from llms import build_llm
from utils.output_parser import extract_code


def sum_scores(score_list):
    # 初始化Agent 1和Agent 2的总分
    total_score_agent1 = 0
    total_score_agent2 = 0
    agent1_pass_list = []
    agent2_pass_list = []
    # 遍历列表中的每一项
    broken = set()
    for item in score_list:
        try:
            score_dict = item["Decision"]
            agent1_score = int(score_dict["ReasoningQuality"]["Agent1"]) + int(
                score_dict["CodeQuality"]["Agent1"]
            )
            agent2_score = int(score_dict["ReasoningQuality"]["Agent2"]) + int(
                score_dict["CodeQuality"]["Agent2"]
            )
            agent1_pass = score_dict["Pass"]["Agent1"]
            agent2_pass = score_dict["Pass"]["Agent2"]
            agent1_pass_list.append(agent1_pass)
            agent2_pass_list.append(agent2_pass)
            # 累加到各自的总分
            total_score_agent1 += int(agent1_score)
            total_score_agent2 += int(agent2_score)
        except:
            broken.add(item["index"])

    # 返回Agent 1和Agent 2的总分之和
    agent1_pass_count = agent1_pass_list.count("Pass")
    agent2_pass_count = agent2_pass_list.count("Pass")
    total_len = len(score_list)
    agent1_pass_rate = float(agent1_pass_count) / float(total_len - len(broken))
    agent2_pass_rate = float(agent2_pass_count) / float(total_len - len(broken))
    logger.info(f"{len(broken)} evaluation results are broken: {broken}")
    logger.info(f"total_len: {total_len}")
    return total_score_agent1, total_score_agent2, agent1_pass_rate, agent2_pass_rate


def sort_by_index(lines):
    data = [json.loads(line) for line in lines]
    data = sorted(data, key=lambda x: x["index"])
    lines = [json.dumps(item, ensure_ascii=False, indent=4) for item in data]
    return lines


def main(config_path, output_path):
    logger.info("started")
    config = safe_load(open(config_path, "r"))
    logger.info("config loaded")
    llm = build_llm(config["llm"]["type"], config["llm"]["args"])
    logger.info("llm built")

    user_prompt_template = config["user_prompt"]

    evaluate_system_prompt = config["system_prompt"]

    if os.path.exists(output_path):
        eval_result = [json.loads(line) for line in open(output_path, "r")]
    else:
        eval_result = []
    fout = open(output_path, "a")
    processed_ids = set([item["index"] for item in eval_result])
    file1 = open(config["reference_path"], "r", encoding="utf-8")
    file2 = open(config["result_path"], "r", encoding="utf-8")
    lines1 = file1.readlines()
    lines2 = file2.readlines()
    lines1 = sort_by_index(lines1)
    lines2 = sort_by_index(lines2)
    assert len(lines1) == len(lines2)
    for line1, line2 in zip(lines1, lines2):
        data1 = json.loads(line1)
        if data1["index"] in processed_ids:
            continue
        logger.info(f"evaluating: {data1['index']}")
        rsp, _ = llm.generate(
            messages=[
                {"role": "system", "content": evaluate_system_prompt},
                {
                    "role": "user",
                    "content": user_prompt_template.format(line1=line1, line2=line2),
                },
            ],
        )
        logger.info(f"evaluate result: {rsp}")
        try:
            analysis, decision = extract_code(rsp.content, "```", "```")
            decision = json.loads(decision)
            logger.info(f"Analysis:\n{analysis}")
            logger.info(f"Decision:\n{decision}")
            eval_item = {
                "Analysis": analysis,
                "Decision": decision,
                "Reference": line1,
                "Result": line2,
                "index": data1["index"],
            }
            eval_result.append(eval_item)
            print(json.dumps(eval_item, ensure_ascii=False), file=fout)
        except:
            continue
    total_score_agent1, total_score_agent2, agent1_pass_rate, agent2_pass_rate = (
        sum_scores(eval_result)
    )
    logger.info("evaluation finished")
    logger.info(
        f"Agent1, total score: {total_score_agent1}, pass rate: {agent1_pass_rate}"
    )
    logger.info(
        f"Agent2, total score: {total_score_agent2}, pass rate: {agent2_pass_rate}"
    )
    logger.info(f"Agent1: {config["reference_path"]}")
    logger.info(f"Agent2: {config["result_path"]}")


if __name__ == "__main__":
    fire.Fire(main)

import json

from loguru import logger
from yaml import safe_load

from llms import build_llm
from utils.output_parser import extract_code
import fire


def sum_scores(score_list):
    # 初始化Agent 1和Agent 2的总分
    total_score_agent1 = 0
    total_score_agent2 = 0
    agent1_pass_list = []
    agent2_pass_list = []
    # 遍历列表中的每一项
    for item in score_list:
        score_dict = item["Decision"]
        agent1_score = (
            score_dict["ReasoningQuality"]["Agent1"]
            + score_dict["CodeQuality"]["Agent1"]
        )
        agent2_score = (
            score_dict["ReasoningQuality"]["Agent2"]
            + score_dict["CodeQuality"]["Agent2"]
        )
        agent1_pass = score_dict["Pass"]["Agent1"]
        agent2_pass = score_dict["Pass"]["Agent2"]
        agent1_pass_list.append(agent1_pass)
        agent2_pass_list.append(agent2_pass)
        # 累加到各自的总分
        total_score_agent1 += int(agent1_score)
        total_score_agent2 += int(agent2_score)

    # 返回Agent 1和Agent 2的总分之和
    agent1_pass_count = agent1_pass_list.count("Pass")
    agent2_pass_count = agent2_pass_list.count("Pass")
    total_len = len(score_list)
    agent1_pass_rate = float(agent1_pass_count) / float(total_len)
    agent2_pass_rate = float(agent2_pass_count) / float(total_len)
    return total_score_agent1, total_score_agent2, agent1_pass_rate, agent2_pass_rate


def main(config_path):
    logger.info("started")
    config = safe_load(open(config_path, "r"))
    logger.info("config loaded")
    llm = build_llm(config["llm"]["type"], config["llm"]["args"])
    logger.info("llm built")

    user_prompt_template = config["user_prompt"]

    evaluate_system_prompt = config["system_prompt"]

    eval_result = []
    file1 = open(config["reference_path"], "r", encoding="utf-8")
    file2 = open(config["result_path"], "r", encoding="utf-8")
    lines1 = file1.readlines()
    lines2 = file2.readlines()
    assert len(lines1) == len(lines2)
    for line1, line2 in zip(lines1, lines2):
        rsp = llm.generate(
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
            logger.info("Analysis:\n" + analysis)
            logger.info("Decision:\n" + decision)
            eval_result.append(
                {
                    "Analysis": analysis,
                    "Decision": decision,
                }
            )
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


if __name__ == "__main__":
    fire.Fire(main)

import re
import os
import matplotlib.pyplot as plt


def plot_loss_curve(
    log_path: str,
    save_path: str = "training_loss.png",
    show: bool = False,
):
    """
    从训练日志中解析 step 和 loss，并绘制 / 保存 loss 曲线
    """
    if not os.path.exists(log_path):
        raise FileNotFoundError(f"Log file not found: {log_path}")

    steps = []
    losses = []

    pattern = re.compile(r"\((\d+)/\d+\).*?loss:([0-9.]+)")

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                steps.append(int(match.group(1)))
                losses.append(float(match.group(2)))

    if not steps:
        raise ValueError("No valid loss data found in log file.")

    # 绘图
    plt.figure(figsize=(8, 5))
    plt.plot(steps, losses, label="Loss")
    plt.xlabel("Training Step")
    plt.ylabel("Loss")
    plt.title("Training Loss Curve")
    plt.grid(True)
    plt.legend()

    # 保存到本地
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"Loss curve saved to: {save_path}")

    if show:
        plt.show()
    else:
        plt.close()


if __name__ == "__main__":
    plot_loss_curve(
        log_path="train.log",
        save_path="training_loss.png",
        show=False,  # 服务器/无GUI环境建议 False
    )

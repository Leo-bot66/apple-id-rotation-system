import { useEffect, useState } from "react";

const demoAccounts = [
  { id: "qa-001", region: "美区演示", email: "qa-001@example.test", password: "demo-only-qa-001", updated: "刚刚" },
  { id: "qa-002", region: "美区演示", email: "qa-002@example.test", password: "demo-only-qa-002", updated: "2 分钟前" },
  { id: "qa-003", region: "美区演示", email: "qa-003@example.test", password: "demo-only-qa-003", updated: "4 分钟前" },
  { id: "qa-004", region: "美区演示", email: "qa-004@example.test", password: "demo-only-qa-004", updated: "6 分钟前" },
  { id: "qa-005", region: "美区演示", email: "qa-005@example.test", password: "demo-only-qa-005", updated: "8 分钟前" },
  { id: "qa-006", region: "美区演示", email: "qa-006@example.test", password: "demo-only-qa-006", updated: "10 分钟前" },
];

function ArrowIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

function WarningIcon() {
  return (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 1.732 1.732 1.732Z" />
    </svg>
  );
}

function UsageNoticeModal({ onClose }) {
  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div className="usage-notice-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="usage-notice-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="usage-notice-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <h2 id="usage-notice-title">安全使用须知</h2>
        <button className="usage-notice-close" type="button" onClick={onClose} aria-label="关闭使用须知">
          <span aria-hidden="true">×</span>
        </button>
        <div className="usage-notice-content">
          <p>本页面只展示虚构的测试账号，不连接任何真实第三方账号服务。</p>
          <ul>
            <li>仅管理你拥有或明确获准使用的测试资产。</li>
            <li>不要在前端、日志或代码仓库中存放真实凭据。</li>
            <li>生产接入必须启用最小权限、审计和人工审批。</li>
          </ul>
          <button className="usage-notice-confirm" type="button" onClick={onClose}>我已了解</button>
        </div>
      </section>
    </div>
  );
}

function CopyButton({ value, copyKey, copiedKey, onCopy }) {
  const isCopied = copiedKey === copyKey;
  return (
    <button
      className={`copy-btn${isCopied ? " copied" : ""}`}
      type="button"
      onClick={() => onCopy(value, copyKey)}
      aria-label={`${isCopied ? "已复制" : "复制"}演示值`}
    >
      {isCopied ? "✓ 已复制" : "复制"}
    </button>
  );
}

function DemoCard({ account, copiedKey, onCopy }) {
  return (
    <article className="card">
      <div className="card-header">
        <div className="card-title">{account.region}</div>
        <div className="status">正常</div>
      </div>

      <div className="info-group">
        <div className="info-label">账号</div>
        <div className="info-value-box">
          <span className="info-value">{account.email}</span>
          <CopyButton value={account.email} copyKey={`${account.id}-email`} copiedKey={copiedKey} onCopy={onCopy} />
        </div>
      </div>

      <div className="info-group">
        <div className="info-label">密码</div>
        <div className="info-value-box">
          <span className="info-value masked" aria-label="密码已隐藏">••••••••</span>
          <CopyButton value={account.password} copyKey={`${account.id}-password`} copiedKey={copiedKey} onCopy={onCopy} />
        </div>
      </div>

      <a className="vip-box" href="#demo-notice">
        <div className="vip-box-title">内部测试工具目录</div>
        <div className="vip-arrow"><ArrowIcon /></div>
      </a>

      <a className="vip-box" href="#demo-notice">
        <div className="vip-box-title">凭据合规说明</div>
        <div className="vip-arrow"><ArrowIcon /></div>
      </a>

      <div className="card-footer">更新时间：{account.updated}</div>
    </article>
  );
}

export function App() {
  const [copiedKey, setCopiedKey] = useState(null);
  const [isUsageNoticeOpen, setIsUsageNoticeOpen] = useState(true);

  async function handleCopy(value, copyKey) {
    try {
      await navigator.clipboard.writeText(value);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = value;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
    setCopiedKey(copyKey);
    window.setTimeout(() => setCopiedKey(null), 1800);
  }

  return (
    <>
      {isUsageNoticeOpen && <UsageNoticeModal onClose={() => setIsUsageNoticeOpen(false)} />}
      <main className="page-shell">
      <header className="header">
        <h1>测试账号状态面板</h1>
        <p>内部测试资产演示页 · 不包含真实第三方账号或生产凭据</p>
      </header>

      <section className="top-notice" id="demo-notice" aria-label="安全说明">
        <WarningIcon />
        <span><strong>安全提示：</strong>当前页面仅使用 <code>.example</code> 演示数据，复制按钮不会返回真实账号、密码或验证码。</span>
      </section>

      <a
        className="service-card"
        href="https://nb.tangping.icu/"
        target="_blank"
        rel="noopener noreferrer sponsored"
        aria-label="访问 Newbee 国际机场导航（推广）"
      >
        <span className="s-badge">推广</span>
        <div className="s-content">
          <div className="s-icon">NB</div>
          <div className="s-text">
            <h3>Newbee 国际机场导航</h3>
            <p>官方入口与常用工具导航，收藏后可快速找到最新入口。</p>
          </div>
        </div>
        <div className="s-btn">访问 nb.tangping.icu <span className="vip-arrow"><ArrowIcon /></span></div>
      </a>

      <section className="container" id="demo-cards" aria-label="演示账号列表">
        {demoAccounts.map((account) => (
          <DemoCard key={account.id} account={account} copiedKey={copiedKey} onCopy={handleCopy} />
        ))}
      </section>

      <footer className="disclaimer">
        <p><strong>说明：</strong>本地原型只用于验证前端布局和复制反馈，不连接邮箱或任何远端账号系统。</p>
        <p className="copyright">© 2026 Internal QA Asset Console · Demo only</p>
      </footer>
      </main>
    </>
  );
}

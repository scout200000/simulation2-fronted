<template>
<div class="app" v-cloak>
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">舆</span>
        <div>
          <h1>舆情推演控制台</h1>
          <p>Simulation2 · Vue 控制台</p>
        </div>
      </div>
      <div class="top-status">
        <span class="live-dot" :class="{ off: !liveOk }"></span>
        <span>{{ liveText }}</span>
      </div>
    </header>

    <div class="workspace">
      <aside class="setup">
        <section class="panel">
          <div class="panel-head">
            <div><p class="eyebrow">1 · 事件</p><h2>事件输入</h2></div>
          </div>
          <label class="field"><span>事件正文</span><textarea v-model="eventContent" maxlength="5000"></textarea></label>
          <div class="form-row">
            <label class="field"><span>主题</span>
              <select v-model="eventTopic">
                <option>社会事件</option><option>新闻时事</option><option>娱乐</option><option>其他</option>
              </select>
            </label>
            <label class="field"><span>情绪倾向</span>
              <select v-model="eventValence">
                <option value="negative">负面</option><option value="neutral">中性</option><option value="positive">正面</option>
              </select>
            </label>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <div><p class="eyebrow">2 · 公告策略</p><h2>公告内容与策略</h2></div>
            <span class="count">7 项汇总</span>
          </div>
          <label class="field">
            <span>策略菜单</span>
            <select v-model="selectedStrategyId" class="strategy-select">
              <option v-for="row in strategyOverview" :key="row.strategy_id" :value="row.strategy_id">
                {{ row.strategy_name }}
              </option>
            </select>
          </label>
          <div class="selected-strategy-card">
            <div class="strategy-summary">
              <strong>{{ selectedStrategy?.strategy_name || '—' }}</strong>
              <span
                v-if="selectedStrategyId === 'custom' && !customReady"
                class="badge warn"
              >待填写公告</span>
            </div>
            <div v-if="['__all__','no_response'].includes(selectedStrategyId)" class="strategy-empty-note">
              {{ selectedStrategyId === '__all__' ? '依次运行不回应和四种内置公告策略。' : '该策略不发布官方公告。' }}
            </div>
            <template v-else-if="selectedAnnouncement">
              <label class="field">
                <span>公告内容</span>
                <textarea v-model="selectedAnnouncement.text" maxlength="5000"></textarea>
              </label>
              <label class="field">
                <span>声明状态</span>
                <select v-model="selectedAnnouncement.status">
                  <option value="clear">clear</option>
                  <option value="incomplete">incomplete</option>
                  <option value="conflict">conflict</option>
                  <option value="none">none</option>
                </select>
              </label>
            </template>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <div><p class="eyebrow">3 · 时机</p><h2>公告发布时间</h2></div>
          </div>
          <div class="form-row">
            <label class="field"><span>模式</span>
              <select v-model="entryMode">
                <option value="dynamic">动态进场</option>
                <option value="fixed_round">固定轮次</option>
              </select>
            </label>
            <label class="field"><span>固定轮次</span>
              <select v-model.number="entryRound" :disabled="entryMode !== 'fixed_round'">
                <option v-for="n in 9" :key="n" :value="n + 1">第 {{ n + 1 }} 轮</option>
              </select>
            </label>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <div><p class="eyebrow">4 · 暂停追加公告</p><h2>任意轮次追加</h2></div>
          </div>
          <div class="form-row">
            <label class="field"><span>发布轮次</span>
              <select v-model.number="timelineRound">
                <option v-for="n in 9" :key="n" :value="n + 1">第 {{ n + 1 }} 轮</option>
              </select>
            </label>
            <label class="field"><span>状态</span>
              <select v-model="timelineStatus">
                <option value="clear">clear</option><option value="incomplete">incomplete</option><option value="conflict">conflict</option>
              </select>
            </label>
          </div>
          <label class="field"><span>公告内容</span><textarea v-model="timelineText" maxlength="5000"></textarea></label>
          <div class="setup-actions">
            <button class="button primary" :disabled="!canAddAnnouncement()" @click="addAnnouncement">添加到时间线</button>
          </div>
          <div class="timeline-list">
            <div v-if="!timeline.length" class="empty">暂无追加公告</div>
            <div v-for="(item, index) in timeline" :key="item.round" class="timeline-item">
              <b>公告{{ index + 1 }} · 第{{ item.round }}轮</b>
              <span :title="item.official_statement">{{ item.official_statement }}</span>
            </div>
          </div>
        </section>

        <div class="setup-actions">
          <button class="button ghost" :disabled="busy" @click="previewInputs">预览输入</button>
          <button class="button primary" :disabled="busy" @click="createSession">创建会话</button>
        </div>
      </aside>

      <main class="control">
        <section class="panel">
          <div class="panel-head">
            <div><p class="eyebrow">会话</p><h2>{{ session ? (session.mode === 'all' ? '全部策略会话' : '单策略会话') : '尚未创建' }}</h2></div>
            <span class="count">{{ session?.experiment_id || '' }}</span>
          </div>
          <div class="summary-strip">
            <div v-for="card in summaryCards" :key="card[0]" class="summary-card">
              <div class="label">{{ card[0] }}</div><div class="value">{{ card[1] }}</div><div class="detail">{{ card[2] }}</div>
            </div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <div><p class="eyebrow">实时</p><h2>舆情指标</h2></div>
            <span class="count">{{ metricsRows.length }} 轮</span>
          </div>
          <div class="mini-strip">
            <div v-for="card in metricCards" :key="card[0]" class="mini-card">
              <b>{{ typeof card[1] === 'number' ? percent(card[1]) : card[1] }}</b><span>{{ card[0] }}</span>
            </div>
          </div>
          <div class="chart-wrap" @mousemove="handleChartMove" @mouseleave="chartTooltip = null">
            <div class="line-chart" v-html="metricsSvg"></div>
            <div v-if="chartTooltip" class="chart-tooltip" :style="{ left: chartTooltip.left + 'px', top: chartTooltip.top + 'px' }">{{ chartTooltip.text }}</div>
          </div>
        </section>

        <section class="live-grid">
          <article class="panel detail-trigger" @click="openAgent">
            <div class="panel-head"><div><p class="eyebrow">实时</p><h2>Agent 状态</h2></div><span class="count">{{ agents.length }} 个 Agent</span></div>
            <div class="mini-strip">
              <div v-for="card in agentSummary" :key="card[0]" class="mini-card"><b>{{ card[1] }}</b><span>{{ card[0] }}</span></div>
            </div>
          </article>
          <article class="panel detail-trigger" @click="openPool">
            <div class="panel-head"><div><p class="eyebrow">实时</p><h2>舆论池</h2></div><span class="count">{{ comments.length }} 条</span></div>
            <div class="mini-strip">
              <div v-for="card in commentsSummary" :key="card[0]" class="mini-card"><b>{{ card[1] }}</b><span>{{ card[0] }}</span></div>
            </div>
          </article>
        </section>

        <section class="panel">
          <div class="panel-head"><div><p class="eyebrow">运行</p><h2>会话控制</h2></div></div>
          <div class="control-row">
            <button v-if="session?.mode !== 'all'" class="button primary" :disabled="!canStart()" @click="startRun">启动</button>
            <button v-if="session?.mode === 'all'" class="button primary" :disabled="busy || !['created','ready'].includes(session?.phase)" @click="runAll">运行全部策略</button>
            <button class="button" :disabled="!canContinue()" @click="continueRun">继续运行</button>
            <button class="button" :disabled="!canPause()" @click="pauseRun">暂停</button>
            <button class="button" :disabled="!canRollback()" @click="rollbackRun">回滚一步</button>
            <button class="button danger" :disabled="busy || !session" @click="restartRun">重启新批次</button>
          </div>
          <div v-if="busy" class="busy">{{ busyText }}</div>
          <div class="current-strategy">{{ currentStrategyText }}</div>
        </section>

        <section class="panel">
          <div class="panel-head"><div><p class="eyebrow">状态</p><h2>推进状态</h2></div><span class="count">{{ phaseLine }}</span></div>
          <div class="progress-track">
            <div v-for="n in (session?.max_steps || 10)" :key="n" class="step-chip" :class="{ done: n <= (session?.completed_step_count || 0), entry: session?.response_step === n }"></div>
          </div>
        </section>
      </main>
    </div>

    <div v-if="poolOpen" class="drawer-backdrop" @click="poolOpen = false"></div>
    <aside v-if="poolOpen" class="comment-drawer open">
      <div class="drawer-head">
        <div><p class="eyebrow">POOL DETAIL</p><h2>舆论池详情</h2></div>
        <button class="button ghost" @click="poolOpen = false">关闭</button>
      </div>
      <div ref="poolDrawerBody" class="drawer-body">
        <template v-if="poolDetail === null">
          <div class="summary-strip">
            <div v-for="card in commentsSummary" :key="card[0]" class="summary-card"><div class="label">{{ card[0] }}</div><div class="value">{{ card[1] }}</div></div>
          </div>
          <div class="comments-visual" v-html="commentEmotionBlock(comments) + commentCompositionBlock(comments)"></div>
          <div class="comment-list">
            <article v-for="(comment, index) in comments" :key="comment.comment_id || index" class="live-comment clickable" @click="poolDetail = comment">
              <div class="feed-meta" v-html="emotionBadgeHtml(comment.emotion) + (comment.faction ? '<span class=&quot;badge&quot;>' + esc(comment.faction) + '</span>' : '')"></div>
              <p>{{ comment.text }}</p>
            </article>
          </div>
        </template>
        <template v-else>
          <div class="drawer-detail-compact pool-detail-compact">
            <button class="button ghost drawer-back-button" @click="poolDetail = null">返回舆论池</button>
            <p class="pool-detail-text">{{ poolDetail.text }}</p>
            <div class="kv-grid">
              <div class="kv"><b>{{ poolDetail.comment_id || '—' }}</b><span>评论编号</span></div>
              <div class="kv"><b>{{ poolDetail.faction || '—' }}</b><span>派系</span></div>
              <div class="kv"><b>{{ orientationText(poolDetail.orientation) }}</b><span>信息取向</span></div>
              <div class="kv"><b>{{ poolDetail.stance || '—' }}</b><span>立场</span></div>
            </div>
          </div>
        </template>
      </div>
    </aside>

    <div v-if="agentOpen" class="drawer-backdrop" @click="agentOpen = false"></div>
    <aside v-if="agentOpen" class="comment-drawer open">
      <div class="drawer-head">
        <div><p class="eyebrow">AGENT DETAIL</p><h2>Agent 状态</h2></div>
        <button class="button ghost" @click="agentOpen = false">关闭</button>
      </div>
      <div class="drawer-body">
        <template v-if="agentDetail === null">
          <div class="agent-network" :class="{ 'is-live': networkActive, 'has-focus': networkHoverId }">
            <div class="network-toolbar">
              <span class="network-state"><i></i>{{ networkStatusText }}</span>
              <span>{{ agents.length }} 节点 · {{ agentNetworkEdges.length }} 条全连接</span>
            </div>
            <div class="network-stage">
              <svg class="network-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
                <g class="network-base-lines">
                  <line
                    v-for="edge in agentNetworkEdges"
                    :key="'base-' + edge.id"
                    class="network-edge-base"
                    :x1="edge.x1"
                    :y1="edge.y1"
                    :x2="edge.x2"
                    :y2="edge.y2"
                  />
                </g>
                <g class="network-flow-lines">
                  <line
                    v-for="edge in agentNetworkEdges"
                    :key="'flow-' + edge.id"
                    class="network-edge-flow"
                    :class="{ active: isNetworkEdgeActive(edge) }"
                    :x1="edge.x1"
                    :y1="edge.y1"
                    :x2="edge.x2"
                    :y2="edge.y2"
                    :style="networkEdgeStyle(edge)"
                  />
                </g>
              </svg>
              <button
                v-for="agent in agentNetworkNodes"
                :key="agent.agent_id"
                type="button"
                class="network-node"
                :class="{ 'is-commenting': agent.last_action === 'comment', dimmed: networkHoverId && networkHoverId !== agent.agent_id }"
                :style="networkNodeStyle(agent)"
                :title="agent.agent_id"
                @mouseenter="setNetworkHover(agent.agent_id)"
                @mouseleave="setNetworkHover(null)"
                @focus="setNetworkHover(agent.agent_id)"
                @blur="setNetworkHover(null)"
                @click="openAgentDetail(agent)"
              >
                <span class="agent-orb" :style="{ '--orb': emotionColor(agent.current_emotion), '--ring': '#ffffff' }">{{ agent.agent_id.slice(-4) }}</span>
                <small>{{ emotionText(agent.current_emotion) }}</small>
              </button>
              <div v-if="!agents.length" class="empty network-empty">等待 Agent 初始化</div>
            </div>
          </div>
          <div class="timeline-list">
            <div v-for="agent in agents" :key="agent.agent_id" class="timeline-item">
              <b>{{ agent.agent_id.slice(-4) }}</b>
              <span>{{ emotionText(agent.current_emotion) }} · {{ agent.last_comment_faction || '无派系' }}</span>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="drawer-detail-compact agent-detail-compact">
            <button class="button ghost drawer-back-button" @click="agentDetail = null">返回全部 Agent</button>
            <div class="kv-grid">
              <div class="kv"><b>{{ agentDetail.agent_id }}</b><span>Agent</span></div>
              <div class="kv"><b>{{ emotionText(agentDetail.current_emotion) }}</b><span>情绪</span></div>
              <div class="kv"><b>{{ agentDetail.last_comment_faction || '—' }}</b><span>评论派系</span></div>
            </div>
            <p class="live-comment">{{ agentDetail.last_comment || '本轮未发表评论' }}</p>
          </div>
        </template>
      </div>
    </aside>
  </div>
</template>

<script>
import consoleOptions from "../core/consoleOptions.js";

export default {
  ...consoleOptions,
  name: "V1View"
};
</script>

<style src="../styles/v1.css"></style>

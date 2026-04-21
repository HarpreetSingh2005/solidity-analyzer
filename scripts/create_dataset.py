#!/usr/bin/env python3
"""
scripts/create_dataset.py
=========================
Phase 2 Dataset Builder for SESA — Solidity Explainable Static Analyzer

Generates 30 high-quality vulnerable Solidity contracts across three categories:
  - Business Logic  (10 contracts)  — economic invariant violations, flawed reward logic
  - Price Oracle    (10 contracts)  — spot-price manipulation, stale feeds, no bounds
  - Flash Loan      (10 contracts)  — reentrancy, governance attacks, collateral inflation

Run:
    python scripts/create_dataset.py

Output:
    dataset/
    ├── smartbugs/              (empty — clone SmartBugs Curated here later)
    ├── business_logic/         (10 .sol files)
    ├── price_oracle/           (10 .sol files)
    ├── flash_loan/             (10 .sol files)
    └── labels.csv
"""

import os
import csv
from pathlib import Path

# ─── Root of dataset ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
DATASET_DIR  = PROJECT_ROOT / "dataset"

DIRS = [
    DATASET_DIR / "smartbugs",
    DATASET_DIR / "business_logic",
    DATASET_DIR / "price_oracle",
    DATASET_DIR / "flash_loan",
]

# ─── Contract definitions ─────────────────────────────────────────────────────
# Each entry: (relative_path, solidity_source, category, description)

CONTRACTS = []

# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 1: BUSINESS LOGIC (10 contracts)
# ══════════════════════════════════════════════════════════════════════════════

CONTRACTS.append((
    "business_logic/broken_rewards.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Broken Staking Reward Distribution
 * CATEGORY: Business Logic — Division-Before-Multiplication Rounding
 *
 * The reward per share is computed as (totalRewards / totalStaked).
 * When totalStaked is large, integer division floors this to 0, meaning
 * ALL accumulated rewards are silently lost. An attacker can deposit a huge
 * amount before the reward epoch ends to dilute everyone else to zero.
 */
contract BrokenRewards {
    mapping(address => uint256) public staked;
    mapping(address => uint256) public rewardDebt;
    uint256 public totalStaked;
    uint256 public totalRewards;
    uint256 public rewardPerShare; // BUG: fixed-point not used → floors to 0

    function deposit(uint256 amount) external {
        _updateRewardPerShare();
        staked[msg.sender] += amount;
        totalStaked       += amount;
        // BUG: rewardDebt set AFTER totalStaked updated, skews debt calc
        rewardDebt[msg.sender] = rewardPerShare * staked[msg.sender];
    }

    function addRewards(uint256 amount) external {
        totalRewards += amount;
        _updateRewardPerShare();
    }

    function _updateRewardPerShare() internal {
        if (totalStaked == 0) return;
        // BUG: integer division truncates — when totalStaked >> totalRewards, result = 0
        rewardPerShare = totalRewards / totalStaked;
    }

    function claimRewards() external {
        _updateRewardPerShare();
        uint256 pending = rewardPerShare * staked[msg.sender] - rewardDebt[msg.sender];
        rewardDebt[msg.sender] = rewardPerShare * staked[msg.sender];
        // pending will be 0 for almost all users if totalStaked is large
        payable(msg.sender).transfer(pending);
    }

    receive() external payable { totalRewards += msg.value; }
}
""",
    "business_logic",
    "Reward-per-share computed with integer division before multiplication — rewards flood to zero when totalStaked is large"
))

CONTRACTS.append((
    "business_logic/vesting_bypass.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Vesting Cliff Bypass via Token Transfer
 * CATEGORY: Business Logic — Incorrect State Transition
 *
 * The vesting cliff is keyed to msg.sender at deposit time.
 * If tokens are transferable (standard ERC-20), a user can simply
 * transfer their unvested position to a fresh wallet and immediately
 * claim — the new address has no cliff recorded, so `startTime` defaults
 * to 0 and the cliff check passes for any timestamp.
 */
contract VestingBypass {
    struct VestingSchedule {
        uint256 amount;
        uint256 startTime;
        uint256 cliffDuration;  // seconds before any withdrawal allowed
        uint256 totalDuration;
        bool    exists;
    }

    mapping(address => VestingSchedule) public schedules;
    mapping(address => uint256) public balances; // internal "token"

    function createVesting(uint256 amount, uint256 cliff, uint256 total) external {
        require(!schedules[msg.sender].exists, "Already vesting");
        schedules[msg.sender] = VestingSchedule(amount, block.timestamp, cliff, total, true);
        balances[msg.sender]  = amount;
    }

    // BUG: transferring balance moves funds but NOT the vesting schedule
    function transferBalance(address to, uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient");
        balances[msg.sender] -= amount;
        balances[to]         += amount;
        // schedule not transferred — recipient has no schedule → defaults allow full claim
    }

    function withdraw(uint256 amount) external {
        VestingSchedule storage s = schedules[msg.sender];
        // BUG: if no schedule, startTime=0 → cliff always passed, vestedAmount = amount
        uint256 elapsed = block.timestamp - s.startTime;
        require(elapsed >= s.cliffDuration, "Cliff not reached");
        uint256 vestedAmount = s.totalDuration == 0
            ? balances[msg.sender]  // BUG: no duration means 100% vested instantly
            : (s.amount * elapsed) / s.totalDuration;
        require(balances[msg.sender] >= amount && amount <= vestedAmount, "Not vested");
        balances[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
    }

    receive() external payable {}
}
""",
    "business_logic",
    "Vesting cliff bypass: transferring internal balance detaches it from the vesting schedule, allowing immediate withdrawal"
))

CONTRACTS.append((
    "business_logic/fee_rounding.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Fee Rounding-Down to Zero
 * CATEGORY: Business Logic — Integer Truncation Exploit
 *
 * Protocol charges a 0.3% fee. For any trade < 334 wei, the fee rounds
 * down to 0. An attacker can split a large trade into many tiny ones,
 * paying zero fees in total. Also: the fee recipient is set once and
 * never validated, so a malicious deployer can silently redirect fees.
 */
contract FeeRounding {
    uint256 public constant FEE_BPS = 30; // 0.30%
    address public feeRecipient;
    mapping(address => uint256) public balances;

    constructor(address _feeRecipient) {
        feeRecipient = _feeRecipient;
    }

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function swap(address to, uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient");
        // BUG: fee = amount * 30 / 10000 floors to 0 for amount < 334
        uint256 fee = (amount * FEE_BPS) / 10_000;
        uint256 net = amount - fee;

        balances[msg.sender] -= amount;
        balances[to]          += net;

        // BUG: if fee rounds to 0, feeRecipient receives nothing
        if (fee > 0) {
            balances[feeRecipient] += fee;
        }
    }

    function withdraw() external {
        uint256 bal = balances[msg.sender];
        balances[msg.sender] = 0;
        payable(msg.sender).transfer(bal);
    }

    receive() external payable {}
}
""",
    "business_logic",
    "Fee calculation uses integer division that rounds to zero for small amounts, enabling free trades via transaction splitting"
))

CONTRACTS.append((
    "business_logic/governance_doublevote.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Governance Double-Vote via Flash Loan / Transfer
 * CATEGORY: Business Logic — Missing Snapshot on Delegation
 *
 * Votes are counted from live balances at the time of castVote(), NOT
 * from a snapshot taken at proposal creation. A whale (or flash loan attacker)
 * can buy tokens, vote, transfer tokens to a second address, and vote again —
 * effectively double-spending their voting power within one proposal.
 */
contract GovernanceDoubleVote {
    mapping(address => uint256) public tokenBalance;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(uint256 => uint256) public votesFor;
    mapping(uint256 => uint256) public votesAgainst;
    uint256 public proposalCount;
    uint256 public totalSupply = 1_000_000e18;

    constructor() {
        tokenBalance[msg.sender] = totalSupply;
    }

    function transfer(address to, uint256 amount) external {
        require(tokenBalance[msg.sender] >= amount);
        tokenBalance[msg.sender] -= amount;
        tokenBalance[to]         += amount;
    }

    function createProposal() external returns (uint256) {
        // BUG: no snapshot of balances taken here
        return ++proposalCount;
    }

    function castVote(uint256 proposalId, bool support) external {
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        hasVoted[proposalId][msg.sender] = true;

        // BUG: uses LIVE balance — attacker votes, transfers tokens, votes again
        uint256 weight = tokenBalance[msg.sender];
        if (support) votesFor[proposalId]     += weight;
        else         votesAgainst[proposalId] += weight;
    }

    function isProposalPassed(uint256 proposalId) external view returns (bool) {
        return votesFor[proposalId] > totalSupply / 2;
    }
}
""",
    "business_logic",
    "Governance votes counted from live token balance, not a snapshot — allows double-voting by transferring tokens between accounts"
))

CONTRACTS.append((
    "business_logic/escrow_griefing.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Escrow Griefing via Dust Deposit
 * CATEGORY: Business Logic — Incorrect State Invariant
 *
 * The escrow requires an exact ETH amount from the buyer to confirm.
 * Any party can send 1 wei directly to the contract, making the stored
 * balance != expectedAmount forever, permanently griefing the escrow
 * and locking both parties' funds. Additionally, the seller can confirm
 * their own release if the dispute timer expires.
 */
contract EscrowGriefing {
    enum State { AWAITING_PAYMENT, COMPLETE, DISPUTED }

    address public buyer;
    address public seller;
    uint256 public expectedAmount;
    uint256 public createdAt;
    State   public state;

    constructor(address _seller, uint256 _amount) payable {
        buyer          = msg.sender;
        seller         = _seller;
        expectedAmount = _amount;
        createdAt      = block.timestamp;
    }

    function confirmPayment() external payable {
        require(state == State.AWAITING_PAYMENT, "Wrong state");
        // BUG: anyone can grief by sending dust, making balance != expectedAmount
        require(address(this).balance == expectedAmount, "Incorrect amount");
        state = State.COMPLETE;
        payable(seller).transfer(address(this).balance);
    }

    function raiseDispute() external {
        require(msg.sender == buyer || msg.sender == seller, "Not party");
        state = State.DISPUTED;
    }

    // BUG: seller can call this unilaterally after timeout — no arbitration
    function sellerRelease() external {
        require(msg.sender == seller, "Not seller");
        require(block.timestamp > createdAt + 7 days, "Too early");
        payable(seller).transfer(address(this).balance);
    }

    // Accepting any ETH breaks the exact-balance check above
    receive() external payable {}
}
""",
    "business_logic",
    "Escrow griefed by dust ETH deposits breaking exact-balance invariant; seller can self-release after timeout without arbitration"
))

CONTRACTS.append((
    "business_logic/dutch_auction_floor.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Dutch Auction Price Floor Bypass
 * CATEGORY: Business Logic — Missing Floor Enforcement in Price Decay
 *
 * The Dutch auction price decays linearly from startPrice to 0 over
 * auctionDuration. There is no floor price — if nobody bids for long
 * enough, price reaches 0 and the NFT can be bought for free.
 * Additionally, the auction can be extended by the owner who also
 * participates, creating a front-running opportunity.
 */
contract DutchAuctionFloor {
    address public owner;
    uint256 public startPrice;
    uint256 public floorPrice;    // declared but never enforced!
    uint256 public startTime;
    uint256 public auctionDuration;
    address public winner;
    bool    public settled;

    constructor(uint256 _start, uint256 _floor, uint256 _duration) {
        owner           = msg.sender;
        startPrice      = _start;
        floorPrice      = _floor;   // BUG: stored but ignored in currentPrice()
        startTime       = block.timestamp;
        auctionDuration = _duration;
    }

    function currentPrice() public view returns (uint256) {
        if (block.timestamp >= startTime + auctionDuration) return 0; // BUG: should be floorPrice
        uint256 elapsed = block.timestamp - startTime;
        // BUG: linear decay to 0 — floor never applied
        return startPrice - (startPrice * elapsed / auctionDuration);
    }

    function bid() external payable {
        require(!settled, "Auction settled");
        uint256 price = currentPrice();
        require(msg.value >= price, "Bid too low");
        winner   = msg.sender;
        settled  = true;
        // BUG: refund overflow — if price=0, entire msg.value kept by contract
        uint256 refund = msg.value - price;
        if (refund > 0) payable(msg.sender).transfer(refund);
        payable(owner).transfer(price);
    }

    // BUG: owner can delay auction to rebid at a lower price
    function extendAuction(uint256 extra) external {
        require(msg.sender == owner, "Not owner");
        auctionDuration += extra;
    }
}
""",
    "business_logic",
    "Dutch auction floor price is stored but never enforced in price calculation; price decays to 0 allowing free bids"
))

CONTRACTS.append((
    "business_logic/yield_checkpoint.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Missing Yield Checkpoint on Deposit
 * CATEGORY: Business Logic — Retroactive Reward Capture
 *
 * Yield accrues globally as yieldPerToken increases over time.
 * When a user deposits, their rewardDebt should be set to the CURRENT
 * accumulated yield so they don't receive retroactive rewards.
 * The missing checkpoint lets a new depositor claim all past yield
 * immediately after joining the pool.
 */
contract YieldCheckpoint {
    mapping(address => uint256) public deposited;
    mapping(address => uint256) public rewardDebt;
    uint256 public totalDeposited;
    uint256 public yieldPerToken;        // accumulated yield per token (scaled 1e18)
    uint256 public lastUpdateTime;
    uint256 public yieldRate = 1e15;     // 0.001 token per second per token

    function _updateYield() internal {
        if (totalDeposited == 0) { lastUpdateTime = block.timestamp; return; }
        uint256 dt = block.timestamp - lastUpdateTime;
        yieldPerToken   += (dt * yieldRate);
        lastUpdateTime   = block.timestamp;
    }

    function deposit(uint256 amount) external {
        _updateYield();
        deposited[msg.sender]  += amount;
        totalDeposited         += amount;
        // BUG: rewardDebt not updated here — user retroactively earns all past yield
        // FIX: rewardDebt[msg.sender] = yieldPerToken * deposited[msg.sender] / 1e18;
    }

    function claimYield() external {
        _updateYield();
        uint256 gross = (yieldPerToken * deposited[msg.sender]) / 1e18;
        uint256 net   = gross - rewardDebt[msg.sender];
        rewardDebt[msg.sender] = gross;
        payable(msg.sender).transfer(net);
    }

    receive() external payable {}
}
""",
    "business_logic",
    "Yield checkpoint not set on deposit — new depositors retroactively earn all yield accumulated before their entry"
))

CONTRACTS.append((
    "business_logic/nft_reveal_frontrun.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: NFT Reveal Front-Running via Predictable Randomness
 * CATEGORY: Business Logic — Weak Randomness / Front-Running
 *
 * Token traits are assigned using blockhash(block.number - 1) and
 * block.timestamp. Both are known to validators before the reveal
 * transaction is included. A validator (or MEV bot watching the pending tx)
 * can selectively include or reorder the reveal to pick a desirable trait,
 * or simply delay until the right block appears.
 */
contract NFTRevealFrontrun {
    uint256 public constant MAX_SUPPLY = 10_000;
    mapping(uint256 => uint8)  public tokenRarity; // 0=common, 1=rare, 2=legendary
    mapping(uint256 => address) public ownerOf;
    uint256 public nextTokenId;
    uint256 public mintPrice = 0.08 ether;

    function mint() external payable returns (uint256 tokenId) {
        require(nextTokenId < MAX_SUPPLY, "Sold out");
        require(msg.value >= mintPrice, "Wrong price");
        tokenId = nextTokenId++;
        ownerOf[tokenId] = msg.sender;
        // Reveal deferred to revealToken()
    }

    function revealToken(uint256 tokenId) external {
        require(ownerOf[tokenId] == msg.sender, "Not owner");
        // BUG: uses block data know to miner/validator before tx is mined
        uint256 seed = uint256(keccak256(abi.encodePacked(
            blockhash(block.number - 1),   // known at mine time
            block.timestamp,               // manipulable ±15s
            tokenId,
            msg.sender
        )));
        // 1% legendary, 10% rare, 89% common
        uint8 rarity = seed % 100 < 1 ? 2 : (seed % 100 < 11 ? 1 : 0);
        tokenRarity[tokenId] = rarity;
    }
}
""",
    "business_logic",
    "NFT rarity assigned using blockhash and block.timestamp — validators can selectively include reveal transactions to pick rare traits"
))

CONTRACTS.append((
    "business_logic/incorrect_liquidation.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Incorrect Liquidation Health Factor
 * CATEGORY: Business Logic — Flawed Collateral Ratio Check
 *
 * The health factor check compares raw collateral value to debt value
 * without applying the liquidation threshold ratio. A position is
 * considered healthy as long as collateral >= debt in raw terms, but
 * a safe protocol should require collateral >= debt * (1 / threshold).
 * This allows borrowing up to 100% LTV (should be 75%), making every
 * loan instantly under-collateralized by protocol standards.
 */
contract IncorrectLiquidation {
    struct Position {
        uint256 collateral;   // in USD (18 decimals)
        uint256 debt;         // in USD (18 decimals)
    }

    mapping(address => Position) public positions;
    uint256 public constant LIQ_THRESHOLD = 75; // 75% — stored but MISUSED below
    uint256 public constant LIQ_BONUS     = 5;  // 5% bonus to liquidator

    function deposit(uint256 amount) external {
        positions[msg.sender].collateral += amount;
    }

    function borrow(uint256 amount) external {
        positions[msg.sender].debt += amount;
        // BUG: allows borrow up to 100% of collateral instead of 75%
        require(isHealthy(msg.sender), "Unhealthy position");
    }

    function isHealthy(address user) public view returns (bool) {
        Position memory p = positions[user];
        if (p.debt == 0) return true;
        // BUG: should be p.collateral * LIQ_THRESHOLD / 100 >= p.debt
        return p.collateral >= p.debt;   // allows 100% LTV
    }

    function liquidate(address user) external {
        require(!isHealthy(user), "Position is healthy");
        Position storage p = positions[user];
        uint256 bonus        = (p.collateral * LIQ_BONUS) / 100;
        uint256 toSend       = p.debt + bonus;
        // BUG: toSend can exceed p.collateral if collateral barely < debt
        require(p.collateral >= toSend, "Collateral insufficient");
        p.collateral -= toSend;
        p.debt        = 0;
        payable(msg.sender).transfer(toSend);
    }

    receive() external payable {}
}
""",
    "business_logic",
    "Liquidation health check compares raw collateral to debt instead of applying LTV threshold — allows 100% LTV borrowing"
))

CONTRACTS.append((
    "business_logic/bridge_ordering.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Bridge Mint-Before-Verification Ordering
 * CATEGORY: Business Logic — Incorrect Operation Sequence
 *
 * The bridge mints wrapped tokens to the recipient BEFORE verifying
 * the cross-chain proof. If proof verification fails after minting,
 * the tokens have already been distributed but the revert only rolls
 * back the state of THIS function. Because the ERC-20 mint is a
 * separate contract call, it is NOT rolled back — attacker receives
 * free tokens without a valid deposit on the source chain.
 */
interface IERC20Mintable {
    function mint(address to, uint256 amount) external;
    function burn(address from, uint256 amount) external;
}

contract BridgeOrdering {
    IERC20Mintable public wrappedToken;
    mapping(bytes32 => bool) public processedProofs;
    address public oracle;

    constructor(address _token, address _oracle) {
        wrappedToken = IERC20Mintable(_token);
        oracle       = _oracle;
    }

    function bridgeIn(
        address recipient,
        uint256 amount,
        bytes32 proof
    ) external {
        require(!processedProofs[proof], "Proof already used");

        // BUG: mint happens BEFORE proof validation
        // If verifyProof() is a separate external call that can succeed on its
        // own but the internal state check below reverts, the mint is already done
        wrappedToken.mint(recipient, amount);      // ← tokens minted here

        bool valid = _verifyProof(proof, recipient, amount);
        require(valid, "Invalid proof");           // ← reverts BUT mint already happened

        processedProofs[proof] = true;
    }

    function _verifyProof(bytes32 proof, address recipient, uint256 amount)
        internal view returns (bool)
    {
        // Simplified: oracle attests to deposit on source chain
        // In reality this is a Merkle proof or MPC signature
        return proof != bytes32(0); // trivially true for this demo
    }

    function bridgeOut(address from, uint256 amount) external {
        wrappedToken.burn(from, amount);
        // Trigger source-chain release (off-chain in production)
    }
}
""",
    "business_logic",
    "Bridge mints wrapped tokens before proof verification — if verification reverts post-mint, tokens are irreversibly distributed"
))

# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 2: PRICE ORACLE (10 contracts)
# ══════════════════════════════════════════════════════════════════════════════

CONTRACTS.append((
    "price_oracle/spot_price_uniswap.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Uniswap V2 Spot Price as Oracle
 * CATEGORY: Price Oracle — Single-Block Manipulation
 *
 * Reads getReserves() directly from the Uniswap V2 pair to compute price.
 * Within a single transaction, an attacker can use a flash loan to move
 * the reserves drastically (dump one token), call this contract to borrow
 * against the manipulated price, then restore reserves — all in one tx.
 */
interface IUniswapV2Pair {
    function getReserves() external view returns (uint112 r0, uint112 r1, uint32 ts);
}

contract SpotPriceOracle {
    IUniswapV2Pair public immutable pair;
    address        public immutable lendingPool;

    constructor(address _pair, address _pool) {
        pair        = IUniswapV2Pair(_pair);
        lendingPool = _pool;
    }

    // BUG: spot price — manipulatable within a single transaction
    function getPrice() public view returns (uint256) {
        (uint112 r0, uint112 r1,) = pair.getReserves();
        require(r0 > 0 && r1 > 0, "Empty reserves");
        // price of token0 in terms of token1 (scaled 1e18)
        return (uint256(r1) * 1e18) / uint256(r0);
    }

    function getCollateralValue(uint256 tokenAmount) external view returns (uint256) {
        // BUG: price is from manipulatable spot — used to determine borrow limit
        return (tokenAmount * getPrice()) / 1e18;
    }
}
""",
    "price_oracle",
    "Uses Uniswap V2 getReserves() as price oracle — fully manipulatable within a single flash-loan transaction"
))

CONTRACTS.append((
    "price_oracle/stale_chainlink.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Stale Chainlink Price (No Freshness Check)
 * CATEGORY: Price Oracle — Staleness / Missing Validation
 *
 * The Chainlink aggregator is called but the updatedAt timestamp is
 * never checked. During network congestion or Chainlink downtime the
 * oracle may go hours without an update. Any protocol using this price
 * will operate on arbitrarily stale data — enabling profitable liquidations
 * or over-borrowing against an out-of-date valuation.
 */
interface AggregatorV3Interface {
    function latestRoundData() external view returns (
        uint80 roundId, int256 answer, uint256 startedAt,
        uint256 updatedAt, uint80 answeredInRound
    );
    function decimals() external view returns (uint8);
}

contract StaleChainlink {
    AggregatorV3Interface public immutable priceFeed;
    uint256 public constant MAX_STALENESS = 1 hours; // defined but never enforced

    constructor(address _feed) {
        priceFeed = AggregatorV3Interface(_feed);
    }

    function getPrice() public view returns (int256) {
        (
            uint80  roundId,
            int256  answer,
            ,
            uint256 updatedAt,
            uint80  answeredInRound
        ) = priceFeed.latestRoundData();

        require(answer > 0, "Negative price");
        // BUG: no staleness check — updatedAt could be days ago
        // FIX: require(block.timestamp - updatedAt <= MAX_STALENESS, "Stale price");

        // BUG: no round completeness check
        // FIX: require(answeredInRound >= roundId, "Incomplete round");

        return answer;
    }

    function assetValue(uint256 amount) external view returns (uint256) {
        int256 price = getPrice();
        return (amount * uint256(price)) / (10 ** priceFeed.decimals());
    }
}
""",
    "price_oracle",
    "Chainlink latestRoundData() called without staleness or round-completeness checks — stale prices accepted silently"
))

CONTRACTS.append((
    "price_oracle/self_referential.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Self-Referential Price Oracle
 * CATEGORY: Price Oracle — Circular / Manipulatable Reserve Ratio
 *
 * The protocol uses its own internal ETH:Token reserve ratio as the price
 * oracle. This is the same pool that users trade against. Anyone who can
 * perform a large trade (or flash loan) can set an arbitrary price, then
 * use that price to borrow inflated amounts from the lending module.
 */
contract SelfReferentialOracle {
    uint256 public ethReserve;
    uint256 public tokenReserve;
    mapping(address => uint256) public tokenBalance;
    mapping(address => uint256) public ethDeposited;

    // BUG: price is THIS contract's own reserve ratio — directly manipulatable
    function getTokenPrice() public view returns (uint256) {
        require(tokenReserve > 0, "No liquidity");
        return (ethReserve * 1e18) / tokenReserve;  // ETH per token
    }

    function addLiquidity(uint256 tokenAmount) external payable {
        ethReserve   += msg.value;
        tokenReserve += tokenAmount;
        tokenBalance[msg.sender] += tokenAmount;
    }

    // Swap ETH for tokens — also shifts the price!
    function swapEthForTokens(uint256 minTokens) external payable {
        uint256 tokens = (msg.value * tokenReserve) / ethReserve;
        require(tokens >= minTokens, "Slippage");
        ethReserve   += msg.value;
        tokenReserve -= tokens;
        tokenBalance[msg.sender] += tokens;
    }

    // BUG: borrow limit derived from the manipulatable self-referential price
    function borrowAgainstToken(uint256 tokenAmount) external {
        uint256 collateralValue = (tokenAmount * getTokenPrice()) / 1e18;
        uint256 borrowable      = (collateralValue * 75) / 100;
        tokenBalance[msg.sender] -= tokenAmount;
        payable(msg.sender).transfer(borrowable);
    }

    receive() external payable { ethReserve += msg.value; }
}
""",
    "price_oracle",
    "Protocol uses its own reserve ratio as price oracle — trades against the same pool shift the price used for borrowing limits"
))

CONTRACTS.append((
    "price_oracle/twap_short_window.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: TWAP With a 1-Block (No) Window
 * CATEGORY: Price Oracle — Insufficient TWAP Duration
 *
 * The contract implements a TWAP but the window is only 1 block (~12s).
 * A single large trade in the previous block is enough to move the TWAP
 * to an arbitrary value. Real-world TWAP windows should be >= 30 minutes
 * to resist single-block manipulation on Ethereum mainnet.
 */
contract TwapShortWindow {
    struct Observation {
        uint256 timestamp;
        uint256 priceCumulative; // sum of instantaneous prices × seconds
    }

    Observation[2] public observations; // ring buffer of size 2
    uint8  public  head;
    uint256 public constant TWAP_WINDOW = 12; // BUG: 1 block ≈ 12 seconds

    // Called by AMM on every trade to update cumulative price
    function update(uint256 spotPrice) external {
        uint8 next = (head + 1) % 2;
        observations[next] = Observation({
            timestamp:       block.timestamp,
            priceCumulative: observations[head].priceCumulative
                             + spotPrice * (block.timestamp - observations[head].timestamp)
        });
        head = next;
    }

    function getTwap() public view returns (uint256) {
        Observation memory current = observations[head];
        Observation memory prev    = observations[(head + 1) % 2];

        uint256 timeElapsed = current.timestamp - prev.timestamp;
        require(timeElapsed >= TWAP_WINDOW, "Window not elapsed");
        // BUG: with TWAP_WINDOW=12s, one manipulated block fully determines price
        return (current.priceCumulative - prev.priceCumulative) / timeElapsed;
    }
}
""",
    "price_oracle",
    "TWAP window is only 12 seconds (1 block) — a single manipulated trade fully determines the oracle price"
))

CONTRACTS.append((
    "price_oracle/no_bounds_oracle.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Oracle Price With No Sanity Bounds
 * CATEGORY: Price Oracle — Missing Validation / Unbounded Input
 *
 * An admin-controlled oracle updates the price with no minimum or maximum
 * validation. A compromised or malicious admin can set price to 1 wei
 * (making all collateral worthless → mass liquidations) or to uint256 max
 * (making all positions unbounded → unlimited borrowing).
 */
contract NoBoundsOracle {
    address public admin;
    uint256 public price;          // price of collateral token in USD (18 dec)
    uint256 public lastUpdated;

    // Reasonable bounds that are defined but NEVER enforced
    uint256 public constant MIN_PRICE = 1e15;   // $0.001
    uint256 public constant MAX_PRICE = 1e27;   // $1,000,000,000

    constructor(uint256 _initialPrice) {
        admin       = msg.sender;
        price       = _initialPrice;
        lastUpdated = block.timestamp;
    }

    function updatePrice(uint256 _newPrice) external {
        require(msg.sender == admin, "Not admin");
        // BUG: bounds MIN_PRICE / MAX_PRICE defined but never checked
        price       = _newPrice;   // could be 0 or type(uint256).max
        lastUpdated = block.timestamp;
    }

    function getPrice() external view returns (uint256) {
        // BUG: no staleness check either
        return price;
    }

    // Simulate a lending protocol using this oracle
    function getMaxBorrow(uint256 collateralAmount) external view returns (uint256) {
        // BUG: if price = MAX_UINT, multiplication overflows silently
        return collateralAmount * price / 1e18 * 75 / 100;
    }
}
""",
    "price_oracle",
    "Admin-controlled oracle accepts any price with no min/max sanity bounds — malicious admin can trigger mass liquidations or unlimited borrowing"
))

CONTRACTS.append((
    "price_oracle/centralized_oracle.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Fully Centralized Oracle (Single Point of Failure)
 * CATEGORY: Price Oracle — Centralization / No Fallback
 *
 * A single admin wallet controls all price feeds with no time-lock,
 * no multi-sig, no on-chain fallback, and no deviation check between
 * updates. This is the #1 exploit vector in DeFi: compromised deployer
 * key → instant drain of all funds via price manipulation + borrowing.
 */
contract CentralizedOracle {
    address public owner;
    mapping(address => uint256) public prices;      // token → USD price (18 dec)
    mapping(address => uint256) public lastUpdated;

    event PriceUpdated(address indexed token, uint256 price);

    constructor() {
        owner = msg.sender;
    }

    // BUG: single EOA controls all prices, no time-lock, no deviation check
    function setPrice(address token, uint256 price) external {
        require(msg.sender == owner, "Not owner");
        // BUG: no check that price changed by <= X% from previous
        // BUG: no minimum delay between updates
        // BUG: no multi-sig or governance
        prices[token]      = price;
        lastUpdated[token] = block.timestamp;
        emit PriceUpdated(token, price);
    }

    function getPrice(address token) external view returns (uint256) {
        require(prices[token] > 0, "Price not set");
        // BUG: no staleness check — price could be weeks old
        return prices[token];
    }

    // BUG: owner can transfer oracle control to any address with no delay
    function transferOwnership(address newOwner) external {
        require(msg.sender == owner);
        owner = newOwner;
    }
}
""",
    "price_oracle",
    "Single-admin oracle with no time-lock, multi-sig, fallback, or deviation check — compromised key enables instant price manipulation"
))

CONTRACTS.append((
    "price_oracle/decimal_mismatch.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Oracle Decimal Mismatch (Off-by-1e12 Price Error)
 * CATEGORY: Price Oracle — Incorrect Scaling / Unit Confusion
 *
 * Chainlink BTC/USD returns an answer with 8 decimals.
 * USDC has 6 decimals. The protocol assumes both are 18 decimals,
 * resulting in a BTC price that is 10^10 times too large.
 * An attacker deposits 1 USDC (1e6 units), gets priced as if it's
 * 1e18 USDC due to wrong scaling, then borrows the entire protocol.
 */
interface IChainlink {
    function latestRoundData() external view
        returns (uint80, int256, uint256, uint256, uint80);
    function decimals() external view returns (uint8);
}

contract DecimalMismatch {
    IChainlink public btcUsdFeed;
    // BUG: assumes both feed and internal accounting use 18 decimals
    uint256 public constant ASSUMED_DECIMALS = 1e18;

    constructor(address _feed) {
        btcUsdFeed = IChainlink(_feed);
    }

    function getBtcPriceUsd() public view returns (uint256) {
        (, int256 answer,,,) = btcUsdFeed.latestRoundData();
        require(answer > 0, "Bad price");
        // BUG: feed has 8 decimals, not 18 — price is 10^10 times too large
        return uint256(answer); // should be: uint256(answer) * 1e10
    }

    // amount in USDC (6 decimals), price in BTC/USD (8 decimals → scaled wrong)
    function usdcToBtc(uint256 usdcAmount) external view returns (uint256) {
        uint256 btcPrice = getBtcPriceUsd();
        // BUG: units completely mismatched — result is off by 10^22
        return (usdcAmount * ASSUMED_DECIMALS) / btcPrice;
    }

    function maxBorrow(uint256 usdcCollateral) external view returns (uint256) {
        // BUG: wildly inflated collateral value → attacker borrows entire protocol
        return usdcToBtc(usdcCollateral) * 75 / 100;
    }
}
""",
    "price_oracle",
    "Oracle decimals assumed to be 18 but Chainlink BTC/USD has 8 — collateral value inflated by 10^10x enabling unlimited borrowing"
))

CONTRACTS.append((
    "price_oracle/reserve_manipulation.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Reserve-Based Price Without Flash-Loan Guard
 * CATEGORY: Price Oracle — AMM Reserve Manipulation
 *
 * Uses getReserves() from an AMM to compute collateral value.
 * No TWAP, no flash-loan callback guard. A flash-loan attack can:
 * 1. Borrow large amount of token0
 * 2. Dump into AMM → depresses token0 price
 * 3. borrow() against token1 at now-inflated token1 price
 * 4. Repay flash loan → profit = overborrowed amount
 */
interface IPair {
    function getReserves() external view returns (uint112, uint112, uint32);
    function token0() external view returns (address);
}

contract ReserveManipulation {
    IPair   public pair;
    address public token0;
    address public token1;

    mapping(address => uint256) public collateral;
    mapping(address => uint256) public debt;

    constructor(address _pair) {
        pair   = IPair(_pair);
        token0 = IPair(_pair).token0();
    }

    function getToken1Price() public view returns (uint256) {
        (uint112 r0, uint112 r1,) = pair.getReserves();
        // BUG: live getReserves() — manipulatable via flash loan
        return (uint256(r0) * 1e18) / uint256(r1); // price of token1 in token0
    }

    function depositToken1(uint256 amount) external {
        collateral[msg.sender] += amount;
    }

    function borrow(uint256 token0Amount) external {
        uint256 price          = getToken1Price();
        uint256 collateralUsd  = (collateral[msg.sender] * price) / 1e18;
        uint256 maxBorrow      = (collateralUsd * 75) / 100;
        require(token0Amount <= maxBorrow, "Over limit");
        debt[msg.sender] += token0Amount;
        // Transfer token0 to borrower (simplified)
    }
}
""",
    "price_oracle",
    "Borrow limit derived from AMM getReserves() price — flash loan can inflate collateral token price to borrow unlimited token0"
))

CONTRACTS.append((
    "price_oracle/average_two_oracles.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Average of Two Correlated Oracles
 * CATEGORY: Price Oracle — Insufficient Diversification
 *
 * Takes the average of two price feeds for "safety." However, both
 * feeds ultimately derive from the same Uniswap pool (one is a TWAP
 * of the other). Manipulating the underlying pool moves both feeds in
 * the same direction — the average provides zero additional protection.
 */
interface IOracle {
    function getPrice() external view returns (uint256);
}

contract AverageTwoOracles {
    IOracle public oracle1; // Uniswap V2 spot
    IOracle public oracle2; // 1-block TWAP of same pool (see TwapShortWindow.sol)

    uint256 public constant MAX_DEVIATION = 5; // 5% — defined, weakly enforced

    constructor(address _o1, address _o2) {
        oracle1 = IOracle(_o1);
        oracle2 = IOracle(_o2);
    }

    function getPrice() external view returns (uint256) {
        uint256 p1 = oracle1.getPrice();
        uint256 p2 = oracle2.getPrice();

        // BUG: deviation check between correlated feeds is meaningless
        // Both move together when the underlying pool is manipulated
        if (p1 > p2) {
            require((p1 - p2) * 100 / p2 <= MAX_DEVIATION, "Deviation too high");
        } else {
            require((p2 - p1) * 100 / p1 <= MAX_DEVIATION, "Deviation too high");
        }

        // Simple average of two correlated sources — not safer than one
        return (p1 + p2) / 2;
    }
}
""",
    "price_oracle",
    "Averages two price oracles that both derive from the same pool — correlated feeds provide zero manipulation resistance"
))

CONTRACTS.append((
    "price_oracle/cascading_oracle.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Cascading Oracle Dependency
 * CATEGORY: Price Oracle — Transitive Trust / Oracle Chain
 *
 * OracleA depends on OracleB for a conversion rate multiplier.
 * OracleB reads from an AMM pool that is manipulatable.
 * Manipulating OracleB cascades to OracleA, allowing a single flash
 * loan to corrupt the final price used by the lending protocol.
 */
interface IRawOracle {
    function getRate() external view returns (uint256); // returns rate scaled 1e18
}

contract OracleB is IRawOracle {
    // BUG: reads from AMM pool — manipulatable
    address public pool;
    function getRate() external view override returns (uint256) {
        // Simplified: return pool reserve ratio
        (bool ok, bytes memory data) = pool.staticcall(
            abi.encodeWithSignature("getReserves()")
        );
        if (!ok) return 1e18;
        (uint112 r0, uint112 r1,) = abi.decode(data, (uint112, uint112, uint32));
        return (uint256(r1) * 1e18) / uint256(r0);
    }
    constructor(address _pool) { pool = _pool; }
}

contract OracleA {
    IRawOracle public oracleB;     // BUG: depends on manipulatable OracleB
    uint256    public basePrice;   // base asset price (reasonably sourced)

    constructor(address _oracleB, uint256 _base) {
        oracleB   = IRawOracle(_oracleB);
        basePrice = _base;
    }

    function getPrice() external view returns (uint256) {
        uint256 rate = oracleB.getRate(); // BUG: this is the manipulatable AMM rate
        // OracleA price = basePrice * rate — inherits all of OracleB's risk
        return (basePrice * rate) / 1e18;
    }
}
""",
    "price_oracle",
    "Price chain: OracleA multiplies by OracleB which reads from an AMM — single flash loan corrupts OracleB and cascades to OracleA"
))

# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 3: FLASH LOAN (10 contracts)
# ══════════════════════════════════════════════════════════════════════════════

CONTRACTS.append((
    "flash_loan/flashloan_reentrancy.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Flash Loan Reentrancy via Callback
 * CATEGORY: Flash Loan — Reentrancy During Flash Loan Execution
 *
 * The vault issues flash loans and calls onFlashLoan() on the receiver.
 * During that callback, the attacker re-enters withdraw() before
 * the balance is deducted at the end of flashLoan(). The vault's
 * internal balance tracking is not locked during the flash loan.
 */
contract FlashloanReentrancy {
    mapping(address => uint256) public deposits;
    uint256 public totalDeposits;
    bool    private _flashActive;

    function deposit() external payable {
        deposits[msg.sender] += msg.value;
        totalDeposits        += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(deposits[msg.sender] >= amount, "Insufficient");
        deposits[msg.sender] -= amount;
        totalDeposits        -= amount;
        payable(msg.sender).transfer(amount); // CEI: safe on its own
    }

    // BUG: no reentrancy guard — during callback, withdraw() is still callable
    function flashLoan(uint256 amount, address receiver, bytes calldata data) external {
        require(amount <= address(this).balance, "Insufficient liquidity");
        uint256 balBefore = address(this).balance;

        // External call to attacker-controlled receiver ← reentrancy entry point
        (bool ok,) = receiver.call{value: amount}(
            abi.encodeWithSignature("onFlashLoan(uint256,bytes)", amount, data)
        );
        require(ok, "Callback failed");

        // BUG: attacker called withdraw() inside onFlashLoan() — balance already reduced
        require(address(this).balance >= balBefore, "Flash loan not repaid");
    }

    receive() external payable {}
}
""",
    "flash_loan",
    "Flash loan issues funds then calls external receiver without reentrancy guard — attacker withdraws during callback before repayment check"
))

CONTRACTS.append((
    "flash_loan/governance_flashloan.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Governance Attack via Flash-Loaned Voting Tokens
 * CATEGORY: Flash Loan — Single-Block Governance Takeover
 *
 * Governance uses live token balance at vote time (no snapshot).
 * Flash-loaning a majority stake allows passing any proposal in one tx:
 * 1. Flash borrow 51% of governance tokens
 * 2. Create + vote on malicious proposal (e.g., drain() treasury)
 * 3. Execute proposal (no timelock)
 * 4. Repay flash loan
 */
interface IFlashLender {
    function flashLoan(address token, uint256 amount, address receiver) external;
}

contract GovernanceFlashloan {
    mapping(address => uint256) public tokenBalance;
    mapping(uint256 => uint256) public proposalVotes;
    mapping(uint256 => bool)    public proposalPassed;
    mapping(uint256 => address) public proposalTarget;
    mapping(uint256 => bytes)   public proposalCalldata;
    uint256 public proposalCount;
    uint256 public totalSupply = 1_000_000e18;
    address public treasury;

    constructor(address _treasury) {
        treasury = _treasury;
        tokenBalance[msg.sender] = totalSupply;
    }

    function transfer(address to, uint256 amount) external {
        tokenBalance[msg.sender] -= amount;
        tokenBalance[to]         += amount;
    }

    function propose(address target, bytes calldata data) external returns (uint256) {
        uint256 id = ++proposalCount;
        proposalTarget[id]   = target;
        proposalCalldata[id] = data;
        return id;
    }

    // BUG: no snapshot — flash-loaned balance counts
    function vote(uint256 proposalId) external {
        proposalVotes[proposalId] += tokenBalance[msg.sender];
    }

    // BUG: no timelock — execute immediately if >50%
    function execute(uint256 proposalId) external {
        require(proposalVotes[proposalId] > totalSupply / 2, "Not passed");
        require(!proposalPassed[proposalId], "Already executed");
        proposalPassed[proposalId] = true;
        (bool ok,) = proposalTarget[proposalId].call(proposalCalldata[proposalId]);
        require(ok, "Execution failed");
    }
}
""",
    "flash_loan",
    "Governance uses live token balance with no timelock — flash-borrowing 51% enables single-transaction proposal creation, voting, and execution"
))

CONTRACTS.append((
    "flash_loan/price_manipulation_flashloan.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Price Oracle Manipulation via Flash Loan
 * CATEGORY: Flash Loan — AMM Price Manipulation + Oracle Exploit
 *
 * Classic 2024-2025 exploit pattern:
 * 1. Flash borrow large amount of tokenA from Lender
 * 2. Dump tokenA into AMM pool → tokenA price crashes, tokenB price spikes
 * 3. Deposit tokenB as collateral to Lending protocol (price now inflated)
 * 4. Borrow maximum tokenA against inflated tokenB collateral
 * 5. Repay flash loan → keep profit (borrowed tokenA - flash loan fee)
 */
interface IAMM {
    function swap(address tokenIn, uint256 amountIn) external returns (uint256);
    function getSpotPrice(address token) external view returns (uint256);
}

interface ILendingProtocol {
    function depositCollateral(address token, uint256 amount) external;
    function borrow(address token, uint256 amount) external;
}

contract PriceManipulationFlashloan {
    IAMM            public amm;
    ILendingProtocol public lending;

    constructor(address _amm, address _lending) {
        amm     = IAMM(_amm);
        lending = ILendingProtocol(_lending);
    }

    // Entry point: called by flash loan provider
    function onFlashLoan(uint256 flashAmount, address tokenA, address tokenB) external {
        // Step 2: Dump tokenA → inflates tokenB spot price in AMM
        uint256 tokenBReceived = amm.swap(tokenA, flashAmount);

        // Step 3 & 4: deposit tokenB at inflated price, borrow tokenA
        lending.depositCollateral(tokenB, tokenBReceived);
        uint256 borrowedA = (tokenBReceived * amm.getSpotPrice(tokenB) * 75) / (100 * 1e18);
        lending.borrow(tokenA, borrowedA);

        // Step 5: repay flash loan — profit = borrowedA - flashAmount - fee
        // (Repayment logic would transfer tokenA back to flash lender)
    }
}
""",
    "flash_loan",
    "Flash loan funds AMM dump to inflate collateral token price — attacker borrows more than deposited collateral is actually worth"
))

CONTRACTS.append((
    "flash_loan/collateral_inflation.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: LP Token Collateral Inflation via Flash Loan
 * CATEGORY: Flash Loan — Collateral Value Manipulation
 *
 * The lending protocol accepts LP tokens as collateral and values them
 * by computing: lpValue = (pool ETH reserves / LP totalSupply) * lpAmount.
 * Flash-loaning ETH and adding it to the pool before querying value
 * inflates the per-LP price — attacker's LP tokens are suddenly worth
 * much more, enabling over-borrowing.
 */
interface IPool {
    function addLiquidity() external payable returns (uint256 lpTokens);
    function removeLiquidity(uint256 lpTokens) external returns (uint256 eth);
    function ethReserve() external view returns (uint256);
    function totalLpSupply() external view returns (uint256);
}

contract CollateralInflation {
    IPool   public pool;
    address public lending;
    mapping(address => uint256) public lpDeposited;
    mapping(address => uint256) public ethBorrowed;

    constructor(address _pool, address _lending) {
        pool    = _pool;
        lending = _lending;
    }

    function getLpValue(uint256 lpAmount) public view returns (uint256) {
        uint256 ethPerLp = (pool.ethReserve() * 1e18) / pool.totalLpSupply();
        // BUG: ethReserve() reads live state — manipulatable by depositing in same tx
        return (lpAmount * ethPerLp) / 1e18;
    }

    function depositLp(uint256 lpAmount) external {
        lpDeposited[msg.sender] += lpAmount;
    }

    function borrow(uint256 ethAmount) external {
        uint256 collateralValue = getLpValue(lpDeposited[msg.sender]);
        uint256 maxBorrow       = (collateralValue * 75) / 100;
        require(ethAmount <= maxBorrow, "Overcollateralized");
        ethBorrowed[msg.sender] += ethAmount;
        payable(msg.sender).transfer(ethAmount);
    }

    // Attacker: flash borrow ETH → addLiquidity → borrow against inflated LP → removeLiquidity → repay flash
    receive() external payable {}
}
""",
    "flash_loan",
    "LP token value calculated from live pool reserves — flash-depositing ETH inflates LP token price used for borrow limits"
))

CONTRACTS.append((
    "flash_loan/fee_bypass_flashloan.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Protocol Fee Bypass via Circular Flash Loan
 * CATEGORY: Flash Loan — Economic Invariant Violation
 *
 * The protocol charges a 1% fee on withdrawals. An attacker can:
 * 1. Flash borrow enough to cover their withdrawal
 * 2. Deposit the flash-loaned funds (earns shares at current price)
 * 3. Withdraw original position (fee waived because they "just deposited")
 * 4. Repay flash loan with the withdrawn funds
 * Result: original withdrawal is fee-free.
 *
 * The fee waiver condition (deposited in same block) creates the bypass.
 */
contract FeeBypassFlashloan {
    mapping(address => uint256) public shares;
    mapping(address => uint256) public lastDepositBlock;
    uint256 public totalShares;
    uint256 public totalAssets;
    uint256 public constant FEE_BPS = 100; // 1% withdrawal fee

    function deposit() external payable {
        uint256 newShares = totalShares == 0
            ? msg.value
            : (msg.value * totalShares) / totalAssets;
        shares[msg.sender]         += newShares;
        totalShares                += newShares;
        totalAssets                += msg.value;
        lastDepositBlock[msg.sender] = block.number; // BUG: enables fee bypass in same block
    }

    function withdraw(uint256 shareAmount) external {
        require(shares[msg.sender] >= shareAmount, "Insufficient");
        uint256 ethAmount = (shareAmount * totalAssets) / totalShares;
        shares[msg.sender] -= shareAmount;
        totalShares        -= shareAmount;
        totalAssets        -= ethAmount;

        // BUG: fee waived if deposited in this block — easily abused with flash loans
        uint256 fee = (lastDepositBlock[msg.sender] == block.number)
            ? 0
            : (ethAmount * FEE_BPS) / 10_000;
        payable(msg.sender).transfer(ethAmount - fee);
    }

    receive() external payable {}
}
""",
    "flash_loan",
    "Withdrawal fee waived for same-block depositors — circular flash loan (deposit then withdraw) allows fee-free exits"
))

CONTRACTS.append((
    "flash_loan/fake_repayment.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Flash Loan Fake Repayment via Internal Accounting
 * CATEGORY: Flash Loan — Insufficient Repayment Validation
 *
 * The flash loan repayment check compares address(this).balance to a
 * snapshot taken before the loan — but the snapshot is taken AFTER
 * the receiver's callback runs. If the receiver deposits ETH back into
 * THIS contract (which increases address(this).balance), the repayment
 * check passes without the receiver actually sending ETH back.
 * The attacker satisfies the check using the vault's own internal balance.
 */
contract FakeRepayment {
    mapping(address => uint256) public deposits;
    uint256 public totalLiquidity;

    function deposit() external payable {
        deposits[msg.sender] += msg.value;
        totalLiquidity       += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(deposits[msg.sender] >= amount, "Insufficient");
        deposits[msg.sender] -= amount;
        totalLiquidity       -= amount;
        payable(msg.sender).transfer(amount);
    }

    function flashLoan(uint256 amount, address receiver) external {
        require(amount <= address(this).balance, "Insufficient");
        payable(receiver).transfer(amount);

        // BUG: snapshot taken AFTER transfer — receiver can call deposit()
        // to put money back into THIS contract and satisfy the check
        // without actually "repaying" in the economic sense
        uint256 expectedBalance = address(this).balance + amount; // wrong: should be pre-transfer balance
        (bool ok,) = receiver.call(abi.encodeWithSignature("executeOperation(uint256)", amount));
        require(ok, "Callback failed");

        // BUG: attacker called deposit() inside executeOperation() — balance is "restored"
        // but they've actually deposited THEIR OWN funds, not repaid the flash loan
        require(address(this).balance >= totalLiquidity, "Not repaid");
    }

    receive() external payable {}
}
""",
    "flash_loan",
    "Flash loan repayment validated against contract balance that can be satisfied by depositing into the same vault — not a real repayment"
))

CONTRACTS.append((
    "flash_loan/share_inflation.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: ERC-4626 Vault Share Inflation / First Depositor Attack
 * CATEGORY: Flash Loan — Share Price Manipulation
 *
 * Classic vault inflation attack amplified by flash loans:
 * 1. Flash borrow large ETH amount
 * 2. Become first depositor → receive 1 share for 1 ETH
 * 3. Directly donate a huge ETH amount to the vault (no shares minted)
 * 4. New depositor's shares round down to 0 (1 ETH → 0 shares)
 * 5. Withdraw the 1 share → get original ETH + victim's ETH
 * 6. Repay flash loan → profit
 */
contract ShareInflation {
    uint256 public totalAssets;
    uint256 public totalShares;
    mapping(address => uint256) public shares;

    uint256 private constant OFFSET = 0; // BUG: no virtual offset protection

    function deposit() external payable {
        uint256 newShares;
        if (totalShares == 0) {
            newShares = msg.value; // First depositor: 1 share per wei
        } else {
            // BUG: integer division floors to 0 when totalAssets is huge
            newShares = (msg.value * totalShares) / totalAssets;
        }
        require(newShares > 0, "Zero shares"); // BUG: this can be bypassed if victim's tx is the "second" with inflated totalAssets
        shares[msg.sender] += newShares;
        totalShares        += newShares;
        totalAssets        += msg.value;
    }

    // Donate ETH directly — inflates asset/share ratio without minting shares
    // BUG: no protection against direct donation inflating totalAssets
    receive() external payable {
        totalAssets += msg.value;
    }

    function withdraw() external {
        uint256 userShares = shares[msg.sender];
        require(userShares > 0, "No shares");
        uint256 ethAmount          = (userShares * totalAssets) / totalShares;
        shares[msg.sender]  = 0;
        totalShares        -= userShares;
        totalAssets        -= ethAmount;
        payable(msg.sender).transfer(ethAmount);
    }
}
""",
    "flash_loan",
    "ERC-4626 vault with no virtual offset — first depositor donates large amount to inflate price, making subsequent depositors receive 0 shares"
))

CONTRACTS.append((
    "flash_loan/oracle_stuffing.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Oracle TWAP Stuffing via Flash Loan
 * CATEGORY: Flash Loan — TWAP Manipulation Through High-Volume Trading
 *
 * The TWAP oracle updates on every trade. By using a flash loan to execute
 * hundreds of trades in a loop within one transaction, an attacker can
 * set the cumulative price to any desired value. The TWAP then reflects
 * the attacker's chosen price for the entire window period, allowing
 * profitable borrowing during that window.
 */
contract OracleStuffing {
    uint256 public priceCumulative;
    uint256 public lastUpdateTime;
    uint256 public constant WINDOW = 10 minutes;

    constructor() {
        lastUpdateTime = block.timestamp;
    }

    // BUG: called by AMM on every trade — no volume or frequency limit
    function updatePrice(uint256 spotPrice) external {
        uint256 dt         = block.timestamp - lastUpdateTime;
        priceCumulative   += spotPrice * dt;
        lastUpdateTime     = block.timestamp;
    }

    // BUG: attacker can call updatePrice() many times in the same block
    // with different spotPrices (via flash loan → trade loop → each trade calls update)
    // Because dt=0 within same block, this particular example is muted BUT:
    // An attacker can do large trades across multiple blocks during the TWAP window
    // OR stuff the oracle by trading in a loop within EVM (using re-entrant style flash swap)

    function getTwap(uint256 prevCumulative, uint256 prevTime) external view returns (uint256) {
        uint256 elapsed = block.timestamp - prevTime;
        require(elapsed >= WINDOW, "Window not elapsed");
        // BUG: if attacker dominated the cumulative sum, TWAP is attacker-controlled
        return (priceCumulative - prevCumulative) / elapsed;
    }
}
""",
    "flash_loan",
    "TWAP oracle updated on every trade with no rate-limiting — flash loan driven trading loop can dominate cumulative price sum"
))

CONTRACTS.append((
    "flash_loan/crossfunc_reentrancy.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Cross-Function Reentrancy via Flash Loan
 * CATEGORY: Flash Loan — State Inconsistency Between Functions
 *
 * The reentrancy guard only blocks direct recursive calls to withdraw().
 * However, a flash loan callback can call a DIFFERENT function (borrow())
 * which also reads and writes the same state — before withdraw() updates it.
 * Classic pattern: withdraw → external call → borrow (not guarded) → double spend.
 */
contract CrossFuncReentrancy {
    mapping(address => uint256) public deposited;
    mapping(address => uint256) public borrowed;
    bool private _withdrawLocked;         // Only guards withdraw, not borrow

    function deposit() external payable {
        deposited[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(!_withdrawLocked, "Reentrant withdraw");
        require(deposited[msg.sender] >= amount, "Insufficient");
        _withdrawLocked = true;

        // External call before state update ← reentrancy point
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok, "Transfer failed");

        deposited[msg.sender] -= amount; // updated AFTER call
        _withdrawLocked = false;
    }

    // BUG: borrow() not guarded — can be called from within withdraw()'s callback
    function borrow(uint256 amount) external {
        // deposited[msg.sender] still shows old (pre-withdraw) balance here
        uint256 collateral = deposited[msg.sender];
        uint256 maxBorrow  = (collateral * 75) / 100;
        require(borrowed[msg.sender] + amount <= maxBorrow, "Over limit");
        borrowed[msg.sender] += amount;
        payable(msg.sender).transfer(amount);
    }

    receive() external payable {}
}
""",
    "flash_loan",
    "Reentrancy guard only protects withdraw() — cross-function reentrancy allows borrowing against uncleaned deposit balance during withdrawal callback"
))

CONTRACTS.append((
    "flash_loan/liquidity_drain.sol",
    """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: AMM Liquidity Drain via Flash Loan + Sandwich
 * CATEGORY: Flash Loan — Liquidity Pool Drain
 *
 * The AMM uses a constant-product invariant (x*y=k) but does not collect
 * a swap fee. An attacker can use a flash loan to:
 * 1. Drain all of token0 by repeated swaps (k maintained, but all token0 extracted)
 * 2. The last swap at extreme imbalance extracts near-zero token1 per token0
 * 3. Restore token1 to repay flash loan
 * Without fees, there is no economic disincentive — the pool is drained.
 */
contract LiquidityDrain {
    uint256 public reserve0;
    uint256 public reserve1;
    mapping(address => uint256) public lpBalance;
    uint256 public totalLp;

    // BUG: no swap fee — AMM is economically drainable
    function swap0For1(uint256 amount0In) external returns (uint256 amount1Out) {
        require(amount0In > 0, "Zero input");
        // constant product: (r0 + in) * (r1 - out) = r0 * r1
        amount1Out = (reserve1 * amount0In) / (reserve0 + amount0In);
        require(amount1Out > 0, "Zero output");
        reserve0 += amount0In;
        reserve1 -= amount1Out;
        // BUG: no fee → attacker can drain token1 for free via incremental swaps
    }

    function addLiquidity(uint256 amount0, uint256 amount1) external payable {
        reserve0 += amount0;
        reserve1 += amount1;
        uint256 lp = totalLp == 0 ? 1000 : (amount0 * totalLp) / reserve0;
        lpBalance[msg.sender] += lp;
        totalLp               += lp;
    }

    function removeLiquidity(uint256 lp) external {
        require(lpBalance[msg.sender] >= lp, "Insufficient LP");
        uint256 amt0 = (lp * reserve0) / totalLp;
        uint256 amt1 = (lp * reserve1) / totalLp;
        lpBalance[msg.sender] -= lp;
        totalLp               -= lp;
        reserve0              -= amt0;
        reserve1              -= amt1;
        payable(msg.sender).transfer(amt0 + amt1);
    }

    receive() external payable {}
}
""",
    "flash_loan",
    "AMM with no swap fee — attacker uses flash loan to perform repeated constant-product swaps, draining one reserve to near-zero without economic cost"
))

# ─── Label table ──────────────────────────────────────────────────────────────

LABELS = []
for rel_path, _, category, description in CONTRACTS:
    LABELS.append({
        "contract_path": str(Path("dataset") / rel_path),
        "label":         1,     # all generated contracts are vulnerable
        "category":      category,
        "description":   description,
    })

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  SESA Phase 2 — Dataset Builder")
    print("=" * 60)

    # Create directories
    for d in DIRS:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  [DIR]  {d.relative_to(PROJECT_ROOT)}")

    # Write contracts
    print(f"\n  Writing {len(CONTRACTS)} contracts...")
    for rel_path, source, category, _ in CONTRACTS:
        dest = DATASET_DIR / rel_path
        dest.write_text(source, encoding="utf-8")
        print(f"  [SOL]  {rel_path}")

    # Write labels.csv
    labels_path = DATASET_DIR / "labels.csv"
    with open(labels_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["contract_path", "label", "category", "description"])
        writer.writeheader()
        writer.writerows(LABELS)
    print(f"\n  [CSV]  dataset/labels.csv  ({len(LABELS)} rows)")

    print("\n" + "=" * 60)
    print(f"  Done! {len(CONTRACTS)} contracts + labels.csv generated.")
    print()
    print("  NEXT STEPS:")
    print("  1. (Optional) Clone SmartBugs for clean/negative samples:")
    print("     git clone --depth=1 https://github.com/smartbugs/smartbugs-curated dataset/smartbugs")
    print()
    print("  2. Extract ML features:")
    print("     python ml/feature_extractor.py  (or use the Colab notebook)")
    print()
    print("  3. Train the model:")
    print("     Open ml/train_on_colab.ipynb in Google Colab")
    print("     Upload dataset/labels.csv + the .sol files")
    print("     Run all cells -> download model.pkl -> place in ml/")
    print("=" * 60)

if __name__ == "__main__":
    main()

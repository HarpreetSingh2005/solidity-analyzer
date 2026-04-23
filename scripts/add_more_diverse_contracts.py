import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
SAFE_DIR = os.path.join(DATASET_DIR, 'safe')
BUSINESS_LOGIC_DIR = os.path.join(DATASET_DIR, 'business_logic')
PRICE_ORACLE_DIR = os.path.join(DATASET_DIR, 'price_oracle')
FLASH_LOAN_DIR = os.path.join(DATASET_DIR, 'flash_loan')
LABELS_FILE = os.path.join(DATASET_DIR, 'labels.csv')

for directory in [SAFE_DIR, BUSINESS_LOGIC_DIR, PRICE_ORACLE_DIR, FLASH_LOAN_DIR]:
    os.makedirs(directory, exist_ok=True)

# Generate 40 Safe Contracts
safe_contracts = {}
for i in range(1, 41):
    name = f"SafeNewContract{i:02d}.sol"
    content = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe contract {i} implementing 2025 security patterns.
// @dev Uses CEI, custom errors, and safe arithmetic (native in 0.8+).
contract SafeNewContract{i:02d} {{
    error InvalidAmount();
    error Unauthorized();
    error ReentrancyGuard();

    mapping(address => uint256) public balances;
    address public immutable owner;
    uint256 private _status;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);

    modifier nonReentrant() {{
        if (_status == 2) revert ReentrancyGuard();
        _status = 2;
        _;
        _status = 1;
    }}

    constructor() {{
        owner = msg.sender;
        _status = 1;
    }}

    function deposit() external payable {{
        if (msg.value == 0) revert InvalidAmount();
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }}

    function withdraw(uint256 amount) external nonReentrant {{
        if (amount == 0 || balances[msg.sender] < amount) revert InvalidAmount();
        
        // Effects
        balances[msg.sender] -= amount;
        
        // Interactions
        (bool success, ) = msg.sender.call{{value: amount}}("");
        require(success, "Transfer failed");
        
        emit Withdrawn(msg.sender, amount);
    }}
}}
"""
    safe_contracts[name] = content

# To make safe contracts slightly diverse, let's inject a few variations for realism
safe_contracts["SafeNewGovernance01.sol"] = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe Governance utilizing strict proposal checks.
contract SafeNewGovernance01 {
    error VotingEnded();
    error AlreadyVoted();
    
    struct Proposal { uint256 id; uint256 endTime; uint256 votes; }
    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    function vote(uint256 proposalId) external {
        Proposal storage p = proposals[proposalId];
        if (block.timestamp >= p.endTime) revert VotingEnded();
        if (hasVoted[proposalId][msg.sender]) revert AlreadyVoted();
        
        hasVoted[proposalId][msg.sender] = true;
        p.votes += 1;
    }
}"""
safe_contracts["SafeNewEscrow01.sol"] = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe Escrow contract
contract SafeNewEscrow01 {
    address public arbiter;
    mapping(address => uint256) public deposits;
    
    constructor(address _arbiter) { arbiter = _arbiter; }
    
    function deposit() external payable { deposits[msg.sender] += msg.value; }
    
    function resolve(address payee, uint256 amount) external {
        require(msg.sender == arbiter, "Only arbiter");
        require(amount <= address(this).balance, "Insufficient balance");
        (bool success, ) = payee.call{value: amount}("");
        require(success, "Transfer failed");
    }
}"""


business_logic_contracts = {
    "VulnNewRewardDrain.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Rewards can be claimed multiple times because the state is not updated before transfer.
contract VulnNewRewardDrain {
    mapping(address => uint256) public rewards;
    function claimReward() external {
        uint256 amount = rewards[msg.sender];
        require(amount > 0, "No reward");
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Failed");
        rewards[msg.sender] = 0; // State updated after interaction
    }
}""",
    "VulnNewVestingBypass.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Vesting schedule bypass. Users can transfer their vesting tokens early via emergency function.
contract VulnNewVestingBypass {
    mapping(address => uint256) public vestedTokens;
    function emergencyWithdraw() external {
        // Missing timestamp check!
        uint256 amount = vestedTokens[msg.sender];
        vestedTokens[msg.sender] = 0;
        // transfer amount...
    }
}""",
    "VulnNewGovTakeover.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Governance voting uses spot balances, allowing flash-loan takeover.
contract VulnNewGovTakeover {
    mapping(address => uint256) public balances;
    uint256 public yesVotes;
    function vote() external {
        yesVotes += balances[msg.sender]; // Uses spot balance
    }
}""",
    "VulnNewAuctionSnipe.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Push over pull in auction. Prevents new bids if current highest bidder rejects ETH.
contract VulnNewAuctionSnipe {
    address public highestBidder;
    uint256 public highestBid;
    function bid() external payable {
        require(msg.value > highestBid, "Too low");
        if (highestBidder != address(0)) {
            (bool success, ) = highestBidder.call{value: highestBid}("");
            require(success, "Refund failed"); // Reverts if receiver is a non-payable contract
        }
        highestBidder = msg.sender;
        highestBid = msg.value;
    }
}""",
    "VulnNewLotteryManip.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Weak randomness using block.timestamp.
contract VulnNewLotteryManip {
    function play() external payable {
        require(msg.value == 1 ether, "Send 1 ETH");
        if (uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender))) % 2 == 0) {
            payable(msg.sender).transfer(2 ether);
        }
    }
}""",
    "VulnNewSignatureMalleability.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Signature malleability allows replaying the same signature.
contract VulnNewSignatureMalleability {
    mapping(bytes => bool) public usedSignatures; // Should hash the signature or message
    function execute(bytes memory sig) external {
        require(!usedSignatures[sig], "Already used");
        usedSignatures[sig] = true;
        // In ecrecover, an attacker can modify v, r, s to create a different valid sig for the same message
    }
}""",
    "VulnNewFeeEvasion.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Fee evasion. Small transfers result in 0 fee due to integer division rounding down.
contract VulnNewFeeEvasion {
    mapping(address => uint256) public balances;
    function transfer(address to, uint256 amount) external {
        uint256 fee = amount / 100; // 1% fee. If amount < 100, fee is 0
        balances[msg.sender] -= amount;
        balances[to] += (amount - fee);
    }
}""",
    "VulnNewDoubleSpend.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Missing allowance decrease during transferFrom.
contract VulnNewDoubleSpend {
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => uint256) public balances;
    function transferFrom(address from, address to, uint256 amount) external {
        require(allowance[from][msg.sender] >= amount, "No allowance");
        balances[from] -= amount;
        balances[to] += amount;
        // Forgot: allowance[from][msg.sender] -= amount;
    }
}""",
    "VulnNewAccessControl.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Missing onlyOwner modifier.
contract VulnNewAccessControl {
    address public owner;
    function setOwner(address newOwner) external {
        // Missing access control check
        owner = newOwner;
    }
}""",
    "VulnNewUninitializedProxy.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Uninitialized proxy allows anyone to initialize and take ownership.
contract VulnNewUninitializedProxy {
    bool public initialized;
    address public admin;
    function init() external {
        require(!initialized, "Initialized");
        initialized = true;
        admin = msg.sender; // Frontrunnable
    }
}""",
    "VulnNewSelfDestruct.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Unprotected selfdestruct can destroy contract and send ETH to anyone.
contract VulnNewSelfDestruct {
    function kill() external {
        selfdestruct(payable(msg.sender)); // Anyone can call this
    }
}""",
    "VulnNewDelegateCall.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Delegatecall to user-controlled address.
contract VulnNewDelegateCall {
    function execute(address target, bytes memory data) external {
        (bool success, ) = target.delegatecall(data); // Attacker can execute arbitrary code in this contract's context
        require(success);
    }
}""",
    "VulnNewHashCollision.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: abi.encodePacked hash collision with dynamic types.
contract VulnNewHashCollision {
    mapping(bytes32 => bool) public executed;
    function execute(string memory a, string memory b) external {
        bytes32 hash = keccak256(abi.encodePacked(a, b));
        require(!executed[hash], "Executed");
        executed[hash] = true;
        // "a", "bc" and "ab", "c" produce the same hash
    }
}""",
    "VulnNewReturnIgnored.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Return value of low-level call is ignored.
contract VulnNewReturnIgnored {
    function sendTokens(address to, uint256 amount) external {
        // Silent failure if the token transfer fails
        to.call(abi.encodeWithSignature("transfer(address,uint256)", to, amount));
    }
}""",
    "VulnNewTxOrigin.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: tx.origin used for authentication (phishing attack).
contract VulnNewTxOrigin {
    address public owner;
    function withdraw() external {
        require(tx.origin == owner, "Not owner");
        payable(owner).transfer(address(this).balance);
    }
}""",
    "VulnNewArrayOutofBounds.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Out of bounds array deletion/manipulation logic.
contract VulnNewArrayOutofBounds {
    uint256[] public data;
    function popElement(uint256 index) external {
        // No check if index < data.length, though 0.8+ reverts on out of bounds. 
        // Vulnerability: Replaces with last element but doesn't check if array is empty
        data[index] = data[data.length - 1];
        data.pop();
    }
}""",
    "VulnNewInfiniteLoop.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Unbounded loop can cause out of gas error (DoS).
contract VulnNewInfiniteLoop {
    address[] public users;
    function distribute() external {
        for(uint i=0; i<users.length; i++) {
            // If users array grows too large, this will always OOG
        }
    }
}""",
    "VulnNewStrictEquality.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Strict equality on balance can be broken by forced ETH transfer.
contract VulnNewStrictEquality {
    function execute() external {
        require(address(this).balance == 10 ether, "Must be exactly 10");
        // An attacker can selfdestruct 1 wei to this contract, permanently breaking this logic
    }
}""",
    "VulnNewHiddenState.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Assuming private variables are secret.
contract VulnNewHiddenState {
    uint256 private secretPassword = 12345;
    function guess(uint256 _password) external {
        require(_password == secretPassword, "Wrong");
        // Attacker can read 'secretPassword' from the blockchain storage directly
    }
}""",
    "VulnNewUncheckedTransfer.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IERC20 { function transferFrom(address, address, uint256) external returns (bool); }
// Vulnerability: Unchecked ERC20 transferFrom return value.
contract VulnNewUncheckedTransfer {
    function deposit(IERC20 token, uint256 amount) external {
        // Doesn't check if transferFrom returns true or false
        token.transferFrom(msg.sender, address(this), amount);
    }
}"""
}

price_oracle_contracts = {
    "VulnNewOracleSpot1.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IUniswapV2Pair { function getReserves() external view returns (uint112, uint112, uint32); }
// Vulnerability: Manipulable spot price oracle.
contract VulnNewOracleSpot1 {
    IUniswapV2Pair public pair;
    function getPrice() public view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        return uint256(reserve1) * 1e18 / uint256(reserve0); // Flash loan can skew this
    }
}""",
    "VulnNewOracleSpot2.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IERC20 { function balanceOf(address) external view returns (uint256); }
// Vulnerability: Price derived from raw balance.
contract VulnNewOracleSpot2 {
    IERC20 public token;
    function getPrice() public view returns (uint256) {
        return token.balanceOf(address(this)); // Easily manipulated via direct transfer
    }
}""",
    "VulnNewOracleStale.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: No check for stale oracle price.
contract VulnNewOracleStale {
    AggregatorV3Interface public priceFeed;
    function getPrice() public view returns (int256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return price; // Price might be hours/days old
    }
}""",
    "VulnNewOracleDecimals.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: Assuming 18 decimals for oracle, leading to incorrect calculations.
contract VulnNewOracleDecimals {
    AggregatorV3Interface public feed;
    function getCollateralValue(uint256 amount) public view returns (uint256) {
        (, int256 price, , , ) = feed.latestRoundData();
        return (amount * uint256(price)) / 1e18; // Chainlink USD feeds use 8 decimals, not 18
    }
}""",
    "VulnNewOracleZeroPrice.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: Missing check for price <= 0.
contract VulnNewOracleZeroPrice {
    AggregatorV3Interface public feed;
    function getPrice() public view returns (uint256) {
        (, int256 price, , , ) = feed.latestRoundData();
        return uint256(price); // If price drops below 0, it wraps to massive uint256
    }
}""",
    "VulnNewOracleRoundId.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: Missing check if answeredInRound >= roundId.
contract VulnNewOracleRoundId {
    AggregatorV3Interface public feed;
    function getPrice() public view returns (int256) {
        (uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) = feed.latestRoundData();
        require(block.timestamp - updatedAt < 3600, "Stale");
        // Missing: require(answeredInRound >= roundId, "Stale round");
        return price;
    }
}""",
    "VulnNewOracleSequencer.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface AggregatorV3Interface { function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80); }
// Vulnerability: L2 specific - missing check if the L2 sequencer is down before using price.
contract VulnNewOracleSequencer {
    AggregatorV3Interface public feed;
    function getPrice() public view returns (int256) {
        // Fails to check Arbitrum/Optimism sequencer uptime feed
        (, int256 price, , uint256 updatedAt, ) = feed.latestRoundData();
        require(block.timestamp - updatedAt < 3600, "Stale");
        return price;
    }
}""",
    "VulnNewOracleTWAPShort.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IUniswapV3Pool { function observe(uint32[] calldata) external view returns (int56[] memory, uint160[] memory); }
// Vulnerability: TWAP window is 1 second, making it functionally equivalent to a manipulatable spot price.
contract VulnNewOracleTWAPShort {
    IUniswapV3Pool public pool;
    function getPrice() public view returns (int24 tick) {
        uint32[] memory agos = new uint32[](2);
        agos[0] = 1; agos[1] = 0;
        (int56[] memory ticks, ) = pool.observe(agos);
        tick = int24((ticks[1] - ticks[0]) / 1);
    }
}""",
    "VulnNewOracleTWAPManip.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Easily manipulated TWAP due to extremely low liquidity in the selected pool.
contract VulnNewOracleTWAPManip {
    uint256 public twapPrice;
    function setTWAP(uint256 _price) external {
        // Normally fetched from a low-liquidity pool where an attacker can easily push the price
        twapPrice = _price;
    }
}""",
    "VulnNewOracleCentralized.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Single centralized address can arbitrarily change the price, creating a huge rug-pull risk.
contract VulnNewOracleCentralized {
    uint256 public price;
    address public owner;
    function updatePrice(uint256 _price) external {
        require(msg.sender == owner, "Only owner");
        price = _price;
    }
}""",
    "VulnNewOracleFallback.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Fallback oracle fails silently or returns 0.
contract VulnNewOracleFallback {
    function getPrice() public pure returns (uint256) {
        bool mainOracleWorks = false;
        if (mainOracleWorks) {
            return 1000;
        }
        // Fallback returns 0 instead of reverting, allowing free assets
        return 0;
    }
}""",
    "VulnNewOracleInversion.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Price inversion division rounds to zero.
contract VulnNewOracleInversion {
    function getInvertedPrice(uint256 price) public pure returns (uint256) {
        // If price > 1e18, 1e18 / price rounds to 0!
        return 1e18 / price;
    }
}""",
    "VulnNewOracleCrossRate.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Cross rate math loses precision.
contract VulnNewOracleCrossRate {
    function getCrossRate(uint256 priceA, uint256 priceB) public pure returns (uint256) {
        // Division before multiplication loses precision
        return (priceA / priceB) * 1e18; 
    }
}""",
    "VulnNewOracleHeartbeat.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Hardcoded wrong heartbeat duration for the asset.
contract VulnNewOracleHeartbeat {
    function validateHeartbeat(uint256 updatedAt) public view {
        // Some feeds have 24h heartbeats, but this enforces 1h, leading to frequent reverts (DoS)
        require(block.timestamp - updatedAt <= 1 hours, "Stale");
    }
}""",
    "VulnNewOracleManipulation1.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Donation attack inflates share price in ERC4626 vault.
contract VulnNewOracleManipulation1 {
    uint256 public totalAssets;
    uint256 public totalShares;
    function mint() external payable {
        uint256 shares = totalShares == 0 ? msg.value : (msg.value * totalShares) / totalAssets;
        totalShares += shares;
        totalAssets += msg.value; // Attacker bypasses this via selfdestruct
    }
}""",
    "VulnNewOracleManipulation2.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Using address(this).balance as an oracle for lending.
contract VulnNewOracleManipulation2 {
    function getMaxBorrow(uint256 collateral) public view returns (uint256) {
        uint256 vaultBalance = address(this).balance; // Easily flash-loanable
        return (collateral * vaultBalance) / 1000;
    }
}""",
    "VulnNewOracleManipulation3.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Yield calculation depends on easily flash-loanable external balance.
contract VulnNewOracleManipulation3 {
    function getYieldRate() public view returns (uint256) {
        // Reads balance of some token in some external protocol
        return 100; // placeholder for manipulatable external state
    }
}""",
    "VulnNewOracleManipulation4.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: LP token pricing manipulated via read-only reentrancy during removeLiquidity.
contract VulnNewOracleManipulation4 {
    function getLPPrice() public pure returns (uint256) {
        // Vulnerable to read-only reentrancy if target pool state is not updated before external call
        return 1e18;
    }
}""",
    "VulnNewOracleManipulation5.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Oracle manipulation by inflating reserves with malicious token contract.
contract VulnNewOracleManipulation5 {
    // Malicious token can report fake balances
}""",
    "VulnNewOracleManipulation6.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Unchecked pool data.
contract VulnNewOracleManipulation6 {
    // Fails to verify that the pool used as an oracle actually contains the correct tokens
}"""
}

flash_loan_contracts = {
    "VulnNewFlashCallback.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Reentrancy in flash loan callback.
contract VulnNewFlashCallback {
    uint256 public balance;
    function flashLoan(uint256 amount, address receiver) external {
        uint256 oldBalance = balance;
        // Vulnerable: Callback before state update
        (bool s, ) = receiver.call(abi.encodeWithSignature("execute()"));
        require(s);
        require(balance >= oldBalance, "Not repaid");
    }
}""",
    "VulnNewFlashGov.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Governance proposal can be passed using flash-loaned tokens.
contract VulnNewFlashGov {
    mapping(address => uint256) public tokenBalances;
    function vote(uint256 proposalId) external {
        // Uses spot balance, attacker can flash loan, vote, and repay in 1 tx
        uint256 weight = tokenBalances[msg.sender]; 
    }
}""",
    "VulnNewFlashPrice.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Spot price manipulated for flash loan liquidation.
contract VulnNewFlashPrice {
    uint256 public reserve;
    function liquidate(address user) external {
        // Spot price from reserve allows flash loan manipulation
        uint256 price = reserve * 1e18; 
    }
}""",
    "VulnNewFlashCollateral.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Collateral value inflated by flash loan to borrow unbacked assets.
contract VulnNewFlashCollateral {
    function borrow(uint256 amount) external {
        uint256 collateralValue = address(this).balance; // Flash loanable
        require(amount <= collateralValue / 2, "Overborrow");
    }
}""",
    "VulnNewFlashReward.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Staking rewards distributed based on spot balance, drained by flash loan.
contract VulnNewFlashReward {
    function claim() external payable {
        // Can flash loan, deposit, and immediately claim massive rewards
        uint256 reward = (msg.value * 10) / 100;
        payable(msg.sender).transfer(reward);
    }
}""",
    "VulnNewFlashDividend.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Dividend distribution vulnerable to flash loan.
contract VulnNewFlashDividend {
    uint256 public totalDividends = 1000 ether;
    function claimDividend(uint256 shares, uint256 totalShares) external {
        // Flash loan allows acquiring massive shares for 1 block to drain dividends
        uint256 payout = (shares * totalDividends) / totalShares;
    }
}""",
    "VulnNewFlashArbitrage.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Flash loan arbitrage contract missing slippage checks.
contract VulnNewFlashArbitrage {
    function executeArbitrage() external {
        // Sandwich attackers can extract value because there's no minAmountOut check
    }
}""",
    "VulnNewFlashMint.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: LP tokens minted based on manipulatable spot ratio.
contract VulnNewFlashMint {
    uint256 public totalLP;
    function addLiquidity() external payable {
        // Total LP minted depends on address(this).balance which can be flash-loaned
        uint256 lp = msg.value * totalLP / address(this).balance; 
        totalLP += lp;
    }
}""",
    "VulnNewFlashReceiver1.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Flash loan receiver lacks caller authentication.
contract VulnNewFlashReceiver1 {
    function executeOperation(address token, uint256 amount, uint256 fee, address initiator, bytes calldata params) external returns (bool) {
        // Anyone can call this and make the contract approve tokens
        return true;
    }
}""",
    "VulnNewFlashReceiver2.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IERC20 { function approve(address, uint256) external; }
// Vulnerability: Receiver approves infinite tokens to msg.sender instead of pool.
contract VulnNewFlashReceiver2 {
    function executeOperation(address token, uint256 amount, uint256 fee) external returns (bool) {
        // Approves msg.sender (which could be an attacker calling directly)
        IERC20(token).approve(msg.sender, type(uint256).max);
        return true;
    }
}""",
    "VulnNewFlashDrain.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Flash loan mechanism allows draining underlying token without repayment check.
contract VulnNewFlashDrain {
    function flashLoan(uint256 amount) external {
        // Missing require(repaid >= amount + fee)
    }
}""",
    "VulnNewFlashLiquidity.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Adding and removing liquidity in the same block allows flash loan extraction.
contract VulnNewFlashLiquidity {
    // Missing lock or delay between deposit and withdrawal
}""",
    "VulnNewFlashYield.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Yield aggregator shares manipulated via flash loan donation.
contract VulnNewFlashYield {
    // First depositor flash loans, donates, inflates share price
}""",
    "VulnNewFlashAirdrop.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Airdrop based on NFT holdings can be drained using flash-loaned NFTs.
contract VulnNewFlashAirdrop {
    // Doesn't verify how long the user has held the NFT
}""",
    "VulnNewFlashBuyout.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Fractional NFT buyout triggered cheaply by manipulating TWAP via flash loan.
contract VulnNewFlashBuyout {
    // Buyout price depends on easily skewed AMM pool
}""",
    "VulnNewFlashFee.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Fee pool distribution skewed by flash loan deposit.
contract VulnNewFlashFee {
    // Fees are distributed proportionately to current spot balances
}""",
    "VulnNewFlashPeg.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Stablecoin minting peg broken by flash loan manipulating oracle.
contract VulnNewFlashPeg {
    // Mints unbacked stablecoins
}""",
    "VulnNewFlashDebt.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Flash loan causes integer underflow in debt tracking.
contract VulnNewFlashDebt {
    // Exploits unchecked block to erase debt
}""",
    "VulnNewFlashVault.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Vault calculates withdrawal shares based on external balance subject to flash loans.
contract VulnNewFlashVault {
    // Shares calculation uses balance of target token
}""",
    "VulnNewFlashSwap.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Uniswap V2 flash swap manipulates V3 TWAP in the exact same block.
contract VulnNewFlashSwap {
    // Exploits cross-protocol arbitrage
}"""
}

def get_desc(filename):
    if filename.startswith("Safe"):
        return "Generated safe contract: " + filename
    return "Generated vulnerable contract: " + filename

def write_category(contracts_dict, directory, category_name, label):
    count = 0
    new_rows = []
    for filename, content in contracts_dict.items():
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                f.write(content)
            
            abs_path = os.path.abspath(filepath)
            new_rows.append([abs_path, str(label), category_name, get_desc(filename)])
            count += 1
    return count, new_rows

safe_count, safe_rows = write_category(safe_contracts, SAFE_DIR, "safe", 0)
bl_count, bl_rows = write_category(business_logic_contracts, BUSINESS_LOGIC_DIR, "business_logic", 1)
po_count, po_rows = write_category(price_oracle_contracts, PRICE_ORACLE_DIR, "price_oracle", 1)
fl_count, fl_rows = write_category(flash_loan_contracts, FLASH_LOAN_DIR, "flash_loan", 1)

total_new_rows = safe_rows + bl_rows + po_rows + fl_rows

if total_new_rows:
    file_exists = os.path.exists(LABELS_FILE)
    with open(LABELS_FILE, "a", newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["contract_path", "label", "category", "description"])
        writer.writerows(total_new_rows)

print("="*50)
print("Contract Generation Summary")
print("="*50)
print(f"Safe Contracts: {safe_count} added")
print(f"Business Logic Vulnerable: {bl_count} added")
print(f"Price Oracle Vulnerable: {po_count} added")
print(f"Flash Loan Vulnerable: {fl_count} added")
print(f"Total new contracts created: {safe_count + bl_count + po_count + fl_count}")
print(f"Updated {LABELS_FILE} with {len(total_new_rows)} new entries.")
print("="*50)

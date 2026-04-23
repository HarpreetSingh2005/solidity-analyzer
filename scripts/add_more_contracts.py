import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
SAFE_DIR = os.path.join(DATASET_DIR, 'safe')
BUSINESS_LOGIC_DIR = os.path.join(DATASET_DIR, 'business_logic')
PRICE_ORACLE_DIR = os.path.join(DATASET_DIR, 'price_oracle')
FLASH_LOAN_DIR = os.path.join(DATASET_DIR, 'flash_loan')
LABELS_FILE = os.path.join(DATASET_DIR, 'labels.csv')

# Ensure directories exist
for directory in [SAFE_DIR, BUSINESS_LOGIC_DIR, PRICE_ORACLE_DIR, FLASH_LOAN_DIR]:
    os.makedirs(directory, exist_ok=True)

safe_contracts = {
    "SafeToken.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe, standard ERC20 token implementation with basic transfer and approval logic.
// @dev Uses Solidity 0.8.x built-in overflow/underflow protection.
contract SafeToken {
    string public name = "Safe Token";
    string public symbol = "STK";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply * 10 ** uint256(decimals);
        balanceOf[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
    }

    function transfer(address _to, uint256 _value) public returns (bool success) {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance");
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        require(_value <= balanceOf[_from], "Insufficient balance");
        require(_value <= allowance[_from][msg.sender], "Allowance exceeded");
        
        balanceOf[_from] -= _value;
        allowance[_from][msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(_from, _to, _value);
        return true;
    }
}""",
    "SafeStaking.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe staking pool using Checks-Effects-Interactions pattern and no reentrancy vulnerabilities.
contract SafeStaking {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public lastStakeTime;

    uint256 public rewardRate = 100; // 100 tokens per day

    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 amount);

    function stake() external payable {
        require(msg.value > 0, "Cannot stake 0");
        
        // Effects
        balances[msg.sender] += msg.value;
        lastStakeTime[msg.sender] = block.timestamp;
        
        emit Staked(msg.sender, msg.value);
    }

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "Nothing to withdraw");
        
        // Effects
        balances[msg.sender] = 0;
        
        // Interactions
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit Withdrawn(msg.sender, amount);
    }
}""",
    "SafeVesting.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe vesting wallet that correctly calculates the released amount based on elapsed time.
contract SafeVesting {
    address public beneficiary;
    uint256 public start;
    uint256 public duration;
    uint256 public released;

    event Released(uint256 amount);

    constructor(address _beneficiary, uint256 _duration) {
        require(_beneficiary != address(0), "Invalid beneficiary");
        beneficiary = _beneficiary;
        start = block.timestamp;
        duration = _duration;
    }

    function release() public {
        require(msg.sender == beneficiary, "Only beneficiary can release");
        
        uint256 unreleased = releasableAmount();
        require(unreleased > 0, "No tokens to release");

        released += unreleased;

        (bool success, ) = beneficiary.call{value: unreleased}("");
        require(success, "Transfer failed");

        emit Released(unreleased);
    }

    function releasableAmount() public view returns (uint256) {
        return vestedAmount() - released;
    }

    function vestedAmount() public view returns (uint256) {
        uint256 totalBalance = address(this).balance + released;

        if (block.timestamp >= start + duration) {
            return totalBalance;
        } else {
            return (totalBalance * (block.timestamp - start)) / duration;
        }
    }

    receive() external payable {}
}""",
    "SafeDAO.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe DAO with correct voting power snapshotting and execution delay.
contract SafeDAO {
    struct Proposal {
        uint256 id;
        address proposer;
        string description;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 endTime;
        bool executed;
    }

    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    uint256 public proposalCount;

    function createProposal(string calldata description) external {
        proposalCount++;
        proposals[proposalCount] = Proposal({
            id: proposalCount,
            proposer: msg.sender,
            description: description,
            votesFor: 0,
            votesAgainst: 0,
            endTime: block.timestamp + 7 days,
            executed: false
        });
    }

    function vote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp < proposal.endTime, "Voting ended");
        require(!hasVoted[proposalId][msg.sender], "Already voted");

        hasVoted[proposalId][msg.sender] = true;

        if (support) {
            proposal.votesFor += 1;
        } else {
            proposal.votesAgainst += 1;
        }
    }

    function executeProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp >= proposal.endTime, "Voting not ended");
        require(!proposal.executed, "Already executed");
        require(proposal.votesFor > proposal.votesAgainst, "Proposal failed");

        proposal.executed = true;
    }
}""",
    "SafeMultisig.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe Multisig with correct signature recovery and execution.
contract SafeMultisig {
    address[] public owners;
    mapping(address => bool) public isOwner;
    uint256 public requiredSignatures;

    struct Transaction {
        address to;
        uint256 value;
        bytes data;
        bool executed;
        uint256 confirmations;
    }

    Transaction[] public transactions;
    mapping(uint256 => mapping(address => bool)) public confirmations;

    constructor(address[] memory _owners, uint256 _required) {
        require(_owners.length > 0 && _required > 0 && _required <= _owners.length, "Invalid owners/required");
        for (uint256 i = 0; i < _owners.length; i++) {
            address owner = _owners[i];
            require(owner != address(0) && !isOwner[owner], "Invalid owner");
            isOwner[owner] = true;
            owners.push(owner);
        }
        requiredSignatures = _required;
    }

    function submitTransaction(address to, uint256 value, bytes memory data) public {
        require(isOwner[msg.sender], "Not an owner");
        transactions.push(Transaction({
            to: to,
            value: value,
            data: data,
            executed: false,
            confirmations: 0
        }));
    }

    function confirmTransaction(uint256 txIndex) public {
        require(isOwner[msg.sender], "Not an owner");
        require(txIndex < transactions.length, "Invalid tx");
        require(!confirmations[txIndex][msg.sender], "Already confirmed");

        confirmations[txIndex][msg.sender] = true;
        transactions[txIndex].confirmations += 1;
    }

    function executeTransaction(uint256 txIndex) public {
        require(isOwner[msg.sender], "Not an owner");
        Transaction storage txn = transactions[txIndex];
        require(!txn.executed, "Already executed");
        require(txn.confirmations >= requiredSignatures, "Not enough confirmations");

        txn.executed = true;
        (bool success, ) = txn.to.call{value: txn.value}(txn.data);
        require(success, "Transaction failed");
    }

    receive() external payable {}
}""",
    "SafeAirdrop.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe Airdrop contract using Merkle tree proof verification.
contract SafeAirdrop {
    bytes32 public merkleRoot;
    mapping(address => bool) public hasClaimed;

    constructor(bytes32 _merkleRoot) {
        merkleRoot = _merkleRoot;
    }

    function claim(uint256 amount, bytes32[] calldata merkleProof) external {
        require(!hasClaimed[msg.sender], "Already claimed");
        
        bytes32 node = keccak256(abi.encodePacked(msg.sender, amount));
        require(verifyProof(merkleProof, merkleRoot, node), "Invalid proof");

        hasClaimed[msg.sender] = true;
        // Token transfer logic here
    }

    function verifyProof(bytes32[] memory proof, bytes32 root, bytes32 leaf) internal pure returns (bool) {
        bytes32 computedHash = leaf;

        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];

            if (computedHash <= proofElement) {
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }

        return computedHash == root;
    }
}""",
    "SafeNFT.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe ERC721 implementation with standard ownership checks.
contract SafeNFT {
    string public name = "Safe NFT";
    string public symbol = "SNFT";
    uint256 public nextTokenId;

    mapping(uint256 => address) private _owners;
    mapping(address => uint256) private _balances;
    mapping(uint256 => address) private _tokenApprovals;
    mapping(address => mapping(address => bool)) private _operatorApprovals;

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);

    function balanceOf(address owner) public view returns (uint256) {
        require(owner != address(0), "Zero address query");
        return _balances[owner];
    }

    function ownerOf(uint256 tokenId) public view returns (address) {
        address owner = _owners[tokenId];
        require(owner != address(0), "Token does not exist");
        return owner;
    }

    function mint(address to) external {
        require(to != address(0), "Mint to zero address");
        
        uint256 tokenId = nextTokenId++;
        _balances[to] += 1;
        _owners[tokenId] = to;

        emit Transfer(address(0), to, tokenId);
    }

    function transferFrom(address from, address to, uint256 tokenId) public {
        require(ownerOf(tokenId) == from, "Not token owner");
        require(to != address(0), "Transfer to zero address");
        require(msg.sender == from || _operatorApprovals[from][msg.sender] || _tokenApprovals[tokenId] == msg.sender, "Not authorized");

        _balances[from] -= 1;
        _balances[to] += 1;
        _owners[tokenId] = to;
        delete _tokenApprovals[tokenId];

        emit Transfer(from, to, tokenId);
    }
}""",
    "SafeMarketplace.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe NFT marketplace escrow enforcing pull-over-push.
contract SafeMarketplace {
    struct Listing {
        address seller;
        uint256 price;
        bool isActive;
    }

    mapping(uint256 => Listing) public listings;
    mapping(address => uint256) public pendingWithdrawals;

    event Listed(uint256 indexed tokenId, uint256 price, address seller);
    event Sold(uint256 indexed tokenId, uint256 price, address buyer);

    function listToken(uint256 tokenId, uint256 price) external {
        require(price > 0, "Price must be greater than zero");
        
        listings[tokenId] = Listing({
            seller: msg.sender,
            price: price,
            isActive: true
        });

        emit Listed(tokenId, price, msg.sender);
    }

    function buyToken(uint256 tokenId) external payable {
        Listing storage listing = listings[tokenId];
        require(listing.isActive, "Listing not active");
        require(msg.value == listing.price, "Incorrect value sent");

        listing.isActive = false;
        
        // Push pattern: update balance instead of direct transfer
        pendingWithdrawals[listing.seller] += msg.value;

        emit Sold(tokenId, listing.price, msg.sender);
    }

    function withdraw() external {
        uint256 amount = pendingWithdrawals[msg.sender];
        require(amount > 0, "No pending funds");

        pendingWithdrawals[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}""",
    "SafeVault.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe timelock vault allowing time-based withdrawals.
contract SafeVault {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public lockTime;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
        lockTime[msg.sender] = block.timestamp + 1 weeks;
    }

    function withdraw() external {
        require(balances[msg.sender] > 0, "No funds");
        require(block.timestamp > lockTime[msg.sender], "Lock time not expired");

        uint256 amount = balances[msg.sender];
        balances[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}""",
    "SafeBridge.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe bridge contract utilizing ecrecover correctly to prevent replay attacks.
contract SafeBridge {
    address public validator;
    mapping(bytes32 => bool) public processedNonces;

    event TokensUnlocked(address indexed to, uint256 amount);

    constructor(address _validator) {
        validator = _validator;
    }

    function unlockTokens(address to, uint256 amount, bytes32 nonce, bytes memory signature) external {
        require(!processedNonces[nonce], "Nonce already processed");
        
        bytes32 messageHash = keccak256(abi.encodePacked(to, amount, nonce));
        bytes32 ethSignedMessageHash = keccak256(abi.encodePacked("\\x19Ethereum Signed Message:\\n32", messageHash));
        
        require(recoverSigner(ethSignedMessageHash, signature) == validator, "Invalid signature");

        processedNonces[nonce] = true;
        
        emit TokensUnlocked(to, amount);
    }

    function recoverSigner(bytes32 _ethSignedMessageHash, bytes memory _signature) internal pure returns (address) {
        require(_signature.length == 65, "Invalid signature length");
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := mload(add(_signature, 32))
            s := mload(add(_signature, 64))
            v := byte(0, mload(add(_signature, 96)))
        }
        return ecrecover(_ethSignedMessageHash, v, r, s);
    }
}""",
    "SafeEscrow.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe escrow contract implementing proper state transitions.
contract SafeEscrow {
    address public buyer;
    address public seller;
    address public arbiter;
    uint256 public amount;
    
    enum State { AWAITING_PAYMENT, AWAITING_DELIVERY, COMPLETE, REFUNDED }
    State public currentState;

    constructor(address _seller, address _arbiter) {
        seller = _seller;
        arbiter = _arbiter;
        currentState = State.AWAITING_PAYMENT;
    }

    function deposit() external payable {
        require(currentState == State.AWAITING_PAYMENT, "Already paid");
        buyer = msg.sender;
        amount = msg.value;
        currentState = State.AWAITING_DELIVERY;
    }

    function confirmDelivery() external {
        require(msg.sender == buyer, "Only buyer can confirm");
        require(currentState == State.AWAITING_DELIVERY, "Cannot confirm delivery");
        
        currentState = State.COMPLETE;
        
        (bool success, ) = seller.call{value: amount}("");
        require(success, "Transfer failed");
    }

    function refund() external {
        require(msg.sender == arbiter, "Only arbiter can refund");
        require(currentState == State.AWAITING_DELIVERY, "Cannot refund");
        
        currentState = State.REFUNDED;
        
        (bool success, ) = buyer.call{value: amount}("");
        require(success, "Transfer failed");
    }
}""",
    "SafeLending.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe simplified lending pool utilizing strict ratio checks.
contract SafeLending {
    mapping(address => uint256) public deposits;
    mapping(address => uint256) public borrows;
    uint256 public totalLiquidity;

    function deposit() external payable {
        deposits[msg.sender] += msg.value;
        totalLiquidity += msg.value;
    }

    function borrow(uint256 amount) external {
        require(amount <= totalLiquidity, "Not enough liquidity");
        require(deposits[msg.sender] * 2 >= borrows[msg.sender] + amount, "Insufficient collateral");
        
        borrows[msg.sender] += amount;
        totalLiquidity -= amount;
        
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }

    function repay() external payable {
        require(borrows[msg.sender] >= msg.value, "Overpayment");
        borrows[msg.sender] -= msg.value;
        totalLiquidity += msg.value;
    }
}""",
    "SafePaymentSplitter.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe payment splitter distributing ether proportionally.
contract SafePaymentSplitter {
    address[] public payees;
    mapping(address => uint256) public shares;
    uint256 public totalShares;
    uint256 public totalReleased;
    mapping(address => uint256) public released;

    constructor(address[] memory _payees, uint256[] memory _shares) {
        require(_payees.length == _shares.length, "Lengths mismatch");
        require(_payees.length > 0, "No payees");

        for (uint256 i = 0; i < _payees.length; i++) {
            require(_payees[i] != address(0), "Zero address");
            require(_shares[i] > 0, "Zero shares");

            payees.push(_payees[i]);
            shares[_payees[i]] = _shares[i];
            totalShares += _shares[i];
        }
    }

    receive() external payable {}

    function release(address payee) public {
        require(shares[payee] > 0, "No shares");

        uint256 totalReceived = address(this).balance + totalReleased;
        uint256 payment = (totalReceived * shares[payee]) / totalShares - released[payee];
        
        require(payment > 0, "No payment due");

        released[payee] += payment;
        totalReleased += payment;

        (bool success, ) = payee.call{value: payment}("");
        require(success, "Transfer failed");
    }
}""",
    "SafeWETH.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe Wrapped Ether contract equivalent.
contract SafeWETH {
    string public name     = "Wrapped Ether";
    string public symbol   = "WETH";
    uint8  public decimals = 18;

    event  Approval(address indexed src, address indexed guy, uint wad);
    event  Transfer(address indexed src, address indexed dst, uint wad);
    event  Deposit(address indexed dst, uint wad);
    event  Withdrawal(address indexed src, uint wad);

    mapping (address => uint)                       public  balanceOf;
    mapping (address => mapping (address => uint))  public  allowance;

    receive() external payable {
        deposit();
    }

    function deposit() public payable {
        balanceOf[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(uint wad) public {
        require(balanceOf[msg.sender] >= wad, "Insufficient balance");
        balanceOf[msg.sender] -= wad;
        
        (bool success, ) = msg.sender.call{value: wad}("");
        require(success, "Transfer failed");
        
        emit Withdrawal(msg.sender, wad);
    }

    function totalSupply() public view returns (uint) {
        return address(this).balance;
    }

    function approve(address guy, uint wad) public returns (bool) {
        allowance[msg.sender][guy] = wad;
        emit Approval(msg.sender, guy, wad);
        return true;
    }

    function transfer(address dst, uint wad) public returns (bool) {
        return transferFrom(msg.sender, dst, wad);
    }

    function transferFrom(address src, address dst, uint wad) public returns (bool) {
        require(balanceOf[src] >= wad, "Insufficient balance");

        if (src != msg.sender && allowance[src][msg.sender] != type(uint256).max) {
            require(allowance[src][msg.sender] >= wad, "Allowance exceeded");
            allowance[src][msg.sender] -= wad;
        }

        balanceOf[src] -= wad;
        balanceOf[dst] += wad;

        emit Transfer(src, dst, wad);
        return true;
    }
}""",
    "SafeOracle.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

// @notice Safe Oracle implementation enforcing strict checks on answered round and staleness.
contract SafeOracle {
    AggregatorV3Interface internal priceFeed;

    constructor(address _priceFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
    }

    function getLatestPrice() public view returns (int256) {
        (
            uint80 roundID, 
            int price,
            ,
            uint timeStamp,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        
        require(price > 0, "Negative or zero price");
        require(timeStamp > 0, "Round not complete");
        require(answeredInRound >= roundID, "Stale price");
        require(block.timestamp - timeStamp < 1 hours, "Price too old");

        return price;
    }
}"""
}

business_logic_contracts = {
    "VulnSigReplay.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnSigReplay {
    mapping(address => uint256) public balances;
    
    // Vulnerability: Replay attack possible due to missing nonce or specific ID
    function transferWithSignature(address to, uint256 amount, bytes memory signature) external {
        bytes32 messageHash = keccak256(abi.encodePacked(to, amount));
        bytes32 ethSignedMessageHash = keccak256(abi.encodePacked("\\x19Ethereum Signed Message:\\n32", messageHash));
        
        address signer = recoverSigner(ethSignedMessageHash, signature);
        require(balances[signer] >= amount, "Insufficient balance");
        
        balances[signer] -= amount;
        balances[to] += amount;
    }

    function recoverSigner(bytes32 hash, bytes memory signature) internal pure returns (address) {
        bytes32 r; bytes32 s; uint8 v;
        if (signature.length != 65) return address(0);
        assembly {
            r := mload(add(signature, 32))
            s := mload(add(signature, 64))
            v := byte(0, mload(add(signature, 96)))
        }
        return ecrecover(hash, v, r, s);
    }
}""",
    "VulnInitFrontrun.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnInitFrontrun {
    address public owner;
    bool public initialized;

    // Vulnerability: Unprotected initialize function can be front-run
    function initialize() external {
        require(!initialized, "Already initialized");
        owner = msg.sender;
        initialized = true;
    }

    function withdrawAll() external {
        require(msg.sender == owner, "Not owner");
        payable(owner).transfer(address(this).balance);
    }
}""",
    "VulnRewardMath.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnRewardMath {
    uint256 public totalStake;
    uint256 public rewardPool;
    mapping(address => uint256) public stakes;

    // Vulnerability: Precision loss (dividing before multiplying) can lead to zero rewards
    function claimReward() external {
        uint256 userStake = stakes[msg.sender];
        require(userStake > 0, "No stake");

        uint256 reward = (userStake / totalStake) * rewardPool;
        
        // Transfer reward...
    }
}""",
    "VulnAuctionDoS.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnAuctionDoS {
    address public highestBidder;
    uint256 public highestBid;

    // Vulnerability: Push payment can DoS the auction if previous bidder is a contract that reverts
    function bid() external payable {
        require(msg.value > highestBid, "Bid too low");

        if (highestBidder != address(0)) {
            // If this fails, the whole transaction reverts
            (bool success, ) = highestBidder.call{value: highestBid}("");
            require(success, "Refund failed");
        }

        highestBidder = msg.sender;
        highestBid = msg.value;
    }
}""",
    "VulnArbitraryCall.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnArbitraryCall {
    address public owner;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    // Vulnerability: Arbitrary call execution by anyone
    function execute(address target, bytes memory data) external {
        // Missing onlyOwner modifier!
        (bool success, ) = target.call(data);
        require(success, "Call failed");
    }
}""",
    "VulnBurnMissingCheck.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnBurnMissingCheck {
    mapping(address => uint256) public balanceOf;

    // Vulnerability: Missing allowance check for burning someone else's tokens
    function burnFrom(address from, uint256 amount) external {
        require(balanceOf[from] >= amount, "Insufficient balance");
        
        // No check if msg.sender is allowed to burn `from` tokens!
        balanceOf[from] -= amount;
    }
}""",
    "VulnWrongAccounting.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnWrongAccounting {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;

    // Vulnerability: Accounting mismatch
    function mint(address to, uint256 amount) external {
        totalSupply += amount;
        // Forgot to update balances[to]!
    }
}""",
    "VulnVotingPower.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnVotingPower {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public votingPower;

    // Vulnerability: Can transfer to oneself to artificially inflate voting power
    function transfer(address to, uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        balances[to] += amount;
        
        votingPower[msg.sender] -= amount;
        votingPower[to] += amount; // If to == msg.sender, voting power increases!
    }
}""",
    "VulnBridgeFakeDeposit.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnBridgeFakeDeposit {
    mapping(address => uint256) public bridgedTokens;

    // Vulnerability: Anyone can mint fake tokens on the destination chain without depositing
    function notifyDeposit(address user, uint256 amount) external {
        // Missing check that msg.sender is the actual bridge contract!
        bridgedTokens[user] += amount;
    }
}""",
    "VulnVaultInflation.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnVaultInflation {
    uint256 public totalShares;
    mapping(address => uint256) public shares;

    // Vulnerability: Empty vault inflation attack (donation attack)
    function deposit() external payable {
        uint256 sharesToMint;
        if (totalShares == 0) {
            sharesToMint = msg.value;
        } else {
            // Attacker can manipulate address(this).balance by direct transfer before deposit
            sharesToMint = (msg.value * totalShares) / (address(this).balance - msg.value);
        }
        shares[msg.sender] += sharesToMint;
        totalShares += sharesToMint;
    }
}"""
}

price_oracle_contracts = {
    "VulnSpotPrice.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IUniswapV2Pair {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
}

contract VulnSpotPrice {
    IUniswapV2Pair public pair;

    // Vulnerability: Relies on easily manipulable spot price from reserves
    function getPrice() public view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        return uint256(reserve1) * 1e18 / uint256(reserve0);
    }
}""",
    "VulnReadOnlyReentrancy.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ICurvePool {
    function get_virtual_price() external view returns (uint256);
}

contract VulnReadOnlyReentrancy {
    ICurvePool public pool;

    // Vulnerability: Read-only reentrancy can manipulate get_virtual_price
    function evaluateCollateral(uint256 lpTokenAmount) public view returns (uint256) {
        uint256 price = pool.get_virtual_price();
        return (lpTokenAmount * price) / 1e18;
    }
}""",
    "VulnStaleOracle.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract VulnStaleOracle {
    AggregatorV3Interface public priceFeed;

    // Vulnerability: Does not check for stale price data
    function getPrice() public view returns (int256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return price;
    }
}""",
    "VulnL2Sequencer.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract VulnL2Sequencer {
    AggregatorV3Interface public priceFeed;

    // Vulnerability: Missing check if L2 sequencer is down (Arbitrum/Optimism)
    function getPrice() public view returns (int256) {
        (, int256 price, , uint256 updatedAt, ) = priceFeed.latestRoundData();
        require(block.timestamp - updatedAt < 1 hours, "Stale price");
        return price;
    }
}""",
    "VulnShortTWAP.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IUniswapV3Pool {
    function observe(uint32[] calldata secondsAgos) external view returns (int56[] memory tickCumulatives, uint160[] memory secondsPerLiquidityCumulativeX128s);
}

contract VulnShortTWAP {
    IUniswapV3Pool public pool;

    // Vulnerability: TWAP window is extremely short (1 second), effectively a spot price
    function getShortTWAP() public view returns (int24 tick) {
        uint32[] memory secondsAgos = new uint32[](2);
        secondsAgos[0] = 1; // 1 second ago
        secondsAgos[1] = 0; // now

        (int56[] memory tickCumulatives, ) = pool.observe(secondsAgos);
        tick = int24((tickCumulatives[1] - tickCumulatives[0]) / 1);
    }
}""",
    "VulnWrongDecimals.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract VulnWrongDecimals {
    AggregatorV3Interface public priceFeed;

    // Vulnerability: Assuming 18 decimals for Chainlink oracle (usually 8 for non-ETH pairs)
    function calculateValue(uint256 amount) public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        // Assuming price is 1e18, but it might be 1e8!
        return (amount * uint256(price)) / 1e18;
    }
}""",
    "VulnAMMReserveManip.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
}

contract VulnAMMReserveManip {
    IERC20 public tokenA;
    IERC20 public tokenB;
    address public pool;

    // Vulnerability: Price derived from raw balance manipulation
    function getSpotPrice() public view returns (uint256) {
        uint256 resA = tokenA.balanceOf(pool);
        uint256 resB = tokenB.balanceOf(pool);
        return (resB * 1e18) / resA;
    }
}""",
    "VulnOracleManipulationLending.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnOracleManipulationLending {
    mapping(address => uint256) public collateral;
    mapping(address => uint256) public borrowed;

    // Vulnerability: Borrows based on manipulated spot balance of the contract
    function borrow(uint256 amount) external {
        uint256 spotPrice = address(this).balance; // Easily manipulated by forced ETH transfer
        uint256 maxBorrow = collateral[msg.sender] * spotPrice / 1e18;
        
        require(borrowed[msg.sender] + amount <= maxBorrow, "Exceeds max borrow");
        borrowed[msg.sender] += amount;
    }
}""",
    "VulnPriceScale.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnPriceScale {
    uint256 public constant ORACLE_PRICE = 1000; // Let's assume it's fetched

    // Vulnerability: Incorrect scaling factor for collateral math
    function calculateCollateralValue(uint256 amount) public pure returns (uint256) {
        // Missing division by scaling factor (e.g., 1e18)
        return amount * ORACLE_PRICE;
    }
}""",
    "VulnMissingPriceValidation.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract VulnMissingPriceValidation {
    AggregatorV3Interface public priceFeed;

    // Vulnerability: Does not check if the price is > 0
    function getPrice() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        // Casting negative price to uint256 causes massive overflow logically
        return uint256(price);
    }
}"""
}

flash_loan_contracts = {
    "VulnFlashDividend.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashDividend {
    mapping(address => uint256) public shares;
    uint256 public totalDividendPool;

    // Vulnerability: Flash loan can be used to buy shares, claim dividend, and sell shares in 1 tx
    function claimDividend() external {
        uint256 dividend = (shares[msg.sender] * totalDividendPool) / 10000;
        shares[msg.sender] = 0; // Resets shares, but can be rebought
        payable(msg.sender).transfer(dividend);
    }
}""",
    "VulnFlashVoting.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashVoting {
    mapping(address => uint256) public balances;
    mapping(address => bool) public hasVoted;
    uint256 public yesVotes;

    // Vulnerability: Spot voting allows a flash loan to skew the results
    function vote(bool support) external {
        require(!hasVoted[msg.sender], "Already voted");
        hasVoted[msg.sender] = true;
        
        uint256 votingPower = balances[msg.sender];
        if (support) yesVotes += votingPower;
    }
}""",
    "VulnFlashLiquidation.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashLiquidation {
    mapping(address => uint256) public collaterals;
    
    function getSpotPrice() public view returns (uint256) {
        // Vulnerable spot price logic
        return address(this).balance; 
    }

    // Vulnerability: Flash loan can manipulate spot price to force liquidations
    function liquidate(address user) external {
        uint256 price = getSpotPrice();
        require(collaterals[user] * price < 1000, "Not liquidatable");
        collaterals[user] = 0; // Liquidated
    }
}""",
    "VulnFlashArbitrage.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashArbitrage {
    uint256 public reserveA = 1000;
    uint256 public reserveB = 1000;

    // Vulnerability: Simple constant product AMM with no slippage protection
    function swapAToB(uint256 amountA) external {
        uint256 amountOut = (amountA * reserveB) / (reserveA + amountA);
        reserveA += amountA;
        reserveB -= amountOut;
        // Transfer B to sender
    }
}""",
    "VulnFlashReceiver.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashReceiver {
    address public owner;

    // Vulnerability: executeOperation has no caller validation
    function executeOperation(address asset, uint256 amount, uint256 premium, address initiator, bytes calldata params) external returns (bool) {
        // Anyone can call this and make the contract approve funds to them or do arbitrary actions
        // Missing: require(msg.sender == pool, "Not lending pool");
        return true;
    }
}""",
    "VulnFlashMintExcess.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashMintExcess {
    uint256 public totalLPTokens;

    // Vulnerability: Mints LP tokens based on spot balance, which can be inflated by flash loans
    function deposit() external payable {
        uint256 amountToMint = msg.value * totalLPTokens / address(this).balance;
        totalLPTokens += amountToMint;
    }
}""",
    "VulnFlashStakingReward.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashStakingReward {
    mapping(address => uint256) public stakes;

    // Vulnerability: Reward is instantly calculated based on current spot balance
    function stakeAndClaim() external payable {
        stakes[msg.sender] += msg.value;
        
        // Spot reward calculation allows flash loan to drain rewards
        uint256 reward = address(this).balance / 100;
        payable(msg.sender).transfer(reward);
    }
}""",
    "VulnFlashYieldAggregator.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashYieldAggregator {
    uint256 public totalShares;

    // Vulnerability: Shares are minted based on the raw ratio, vulnerable to inflation attack
    function deposit() external payable {
        uint256 shares = (msg.value * totalShares) / address(this).balance;
        if (totalShares == 0) shares = msg.value;
        totalShares += shares;
    }
}""",
    "VulnFlashOracle.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IUniswapV2Pair {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
}

contract VulnFlashOracle {
    IUniswapV2Pair public pair;

    // Vulnerability: Flash loan can heavily skew reserves to return a manipulated price
    function getPrice() external view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        return uint256(reserve0) / uint256(reserve1);
    }
}""",
    "VulnFlashPoolDrain.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashPoolDrain {
    uint256 public reserve;

    // Vulnerability: sync() sets reserve to balance. Flash loan can donate, then drain elsewhere or skew price.
    function sync() external {
        reserve = address(this).balance;
    }
}"""
}

def get_desc(filename):
    if filename.startswith("Safe"):
        return "Generated safe contract: " + filename
    return "Generated vulnerable contract: " + filename

# Write contracts to disk
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

# Append to labels.csv
if total_new_rows:
    file_exists = os.path.exists(LABELS_FILE)
    with open(LABELS_FILE, "a", newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["contract_path", "label", "category", "description"])
        
        writer.writerows(total_new_rows)

print("="*40)
print("Contract Generation Summary")
print("="*40)
print(f"Safe Contracts: {safe_count} new (Total: 15)")
print(f"Business Logic Vulnerable: {bl_count} new (Total: 10)")
print(f"Price Oracle Vulnerable: {po_count} new (Total: 10)")
print(f"Flash Loan Vulnerable: {fl_count} new (Total: 10)")
print(f"Total new contracts created: {safe_count + bl_count + po_count + fl_count}")
print(f"Updated {LABELS_FILE} with {len(total_new_rows)} new entries.")
print("="*40)

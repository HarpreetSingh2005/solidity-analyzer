import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')

os.makedirs(TESTS_DIR, exist_ok=True)

contracts = {
    # ==========================================
    # 5 VULNERABLE CONTRACTS
    # ==========================================
    "TestVulnReentrancy.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Vulnerable to Reentrancy. State is updated after external call.
contract TestVulnReentrancy {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable: Interaction before Effect (violates CEI)
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        balances[msg.sender] -= amount;
    }
}""",
    
    "TestVulnAccessControl.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Vulnerable to Access Control. Missing onlyOwner modifier on destructive function.
contract TestVulnAccessControl {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // Vulnerable: Anyone can call this function and destroy the contract
    function destroy() external {
        selfdestruct(payable(msg.sender));
    }
}""",

    "TestVulnFlashLoan.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Vulnerable to Flash Loan manipulation. Shares rely on manipulatable spot balance.
contract TestVulnFlashLoan {
    uint256 public totalShares;
    
    // Vulnerable: Shares minted based on manipulatable address(this).balance
    function deposit() external payable {
        uint256 shares;
        if (totalShares == 0) {
            shares = msg.value;
        } else {
            // Attacker can flash loan ETH to themselves and force-send it to inflate address(this).balance
            shares = (msg.value * totalShares) / (address(this).balance - msg.value);
        }
        totalShares += shares;
    }
}""",

    "TestVulnPriceOracle.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

// @notice Vulnerable to Stale Price Oracle. Missing freshness checks.
contract TestVulnPriceOracle {
    AggregatorV3Interface public priceFeed;

    constructor(address _feed) {
        priceFeed = AggregatorV3Interface(_feed);
    }

    // Vulnerable: Does not verify if the price is stale, negative, or incomplete
    function getPrice() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return uint256(price);
    }
}""",

    "TestVulnOverflow.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Vulnerable to Integer Underflow via misuse of unchecked block.
contract TestVulnOverflow {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // Vulnerable: Improper use of unchecked block allows balance underflow
    function transfer(address to, uint256 amount) external {
        unchecked {
            // If amount > balances[msg.sender], it underflows and the sender gains massive artificial balance
            balances[msg.sender] -= amount;
            balances[to] += amount;
        }
    }
}""",

    # ==========================================
    # 5 SAFE CONTRACTS
    # ==========================================
    "TestSafeReentrancyGuard.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe against reentrancy using Checks-Effects-Interactions and a lock.
contract TestSafeReentrancyGuard {
    mapping(address => uint256) public balances;
    uint256 private _status = 1;
    error ReentrantCall();

    modifier nonReentrant() {
        if (_status == 2) revert ReentrantCall();
        _status = 2;
        _;
        _status = 1;
    }

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external nonReentrant {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Effect (state changes before external call)
        balances[msg.sender] -= amount;
        
        // Interaction
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}""",

    "TestSafeAccessControl.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe contract demonstrating correct access control pattern.
contract TestSafeAccessControl {
    address public immutable owner;
    error Unauthorized();

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized();
        _;
    }

    // Safe: Only the owner can call this
    function adminAction() external onlyOwner {
        // Critical action
    }
}""",

    "TestSafePriceOracle.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

// @notice Safe oracle consumption with full validation.
contract TestSafePriceOracle {
    AggregatorV3Interface public priceFeed;

    constructor(address _feed) {
        priceFeed = AggregatorV3Interface(_feed);
    }

    function getPrice() public view returns (uint256) {
        (uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();
        
        // Safe: Validating against staleness and negative values
        require(price > 0, "Invalid price");
        require(block.timestamp - updatedAt < 3600, "Stale price");
        require(answeredInRound >= roundId, "Stale round");

        return uint256(price);
    }
}""",

    "TestSafeVault.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe vault avoiding donation inflation attacks by tracking internal state.
contract TestSafeVault {
    uint256 public totalShares;
    uint256 public totalAssets;
    
    // Safe: Tracks totalAssets internally rather than reading address(this).balance, preventing forced ETH attacks
    function deposit() external payable {
        uint256 shares;
        if (totalShares == 0) {
            shares = msg.value;
        } else {
            shares = (msg.value * totalShares) / totalAssets;
        }
        totalShares += shares;
        totalAssets += msg.value;
    }
}""",

    "TestSafeMath.sol": """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe math relying on Solidity 0.8+ native checks.
contract TestSafeMath {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // Safe: Solidity 0.8.x will automatically revert on underflow here without needing SafeMath
    function safeTransfer(address to, uint256 amount) external {
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}"""
}

def generate_tests():
    count_vuln = 0
    count_safe = 0

    for filename, content in contracts.items():
        filepath = os.path.join(TESTS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        if "Vuln" in filename:
            count_vuln += 1
        elif "Safe" in filename:
            count_safe += 1

    print(f"Generated {count_vuln} vulnerable and {count_safe} safe test contracts in tests/ folder.")

if __name__ == "__main__":
    generate_tests()

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

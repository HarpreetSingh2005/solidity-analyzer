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

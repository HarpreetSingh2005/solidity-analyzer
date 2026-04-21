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

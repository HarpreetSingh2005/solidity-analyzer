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

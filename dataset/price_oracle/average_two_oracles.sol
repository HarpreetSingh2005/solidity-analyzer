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

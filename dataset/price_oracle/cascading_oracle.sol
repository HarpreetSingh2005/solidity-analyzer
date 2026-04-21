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

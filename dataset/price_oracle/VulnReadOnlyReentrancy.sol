// SPDX-License-Identifier: MIT
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
}
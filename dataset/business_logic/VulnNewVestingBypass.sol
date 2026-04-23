// SPDX-License-Identifier: MIT
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
}
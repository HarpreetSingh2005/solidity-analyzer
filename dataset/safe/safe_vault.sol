// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeVault {
    mapping(address => uint256) public shares;
    uint256 public totalShares;
    uint256 public totalAssets;

    function deposit() external payable {
        uint256 newShares = totalShares == 0 ? msg.value : (msg.value * totalShares) / totalAssets;
        shares[msg.sender] += newShares;
        totalShares += newShares;
        totalAssets += msg.value;
    }
}
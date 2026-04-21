// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Bridge Mint-Before-Verification Ordering
 * CATEGORY: Business Logic — Incorrect Operation Sequence
 *
 * The bridge mints wrapped tokens to the recipient BEFORE verifying
 * the cross-chain proof. If proof verification fails after minting,
 * the tokens have already been distributed but the revert only rolls
 * back the state of THIS function. Because the ERC-20 mint is a
 * separate contract call, it is NOT rolled back — attacker receives
 * free tokens without a valid deposit on the source chain.
 */
interface IERC20Mintable {
    function mint(address to, uint256 amount) external;
    function burn(address from, uint256 amount) external;
}

contract BridgeOrdering {
    IERC20Mintable public wrappedToken;
    mapping(bytes32 => bool) public processedProofs;
    address public oracle;

    constructor(address _token, address _oracle) {
        wrappedToken = IERC20Mintable(_token);
        oracle       = _oracle;
    }

    function bridgeIn(
        address recipient,
        uint256 amount,
        bytes32 proof
    ) external {
        require(!processedProofs[proof], "Proof already used");

        // BUG: mint happens BEFORE proof validation
        // If verifyProof() is a separate external call that can succeed on its
        // own but the internal state check below reverts, the mint is already done
        wrappedToken.mint(recipient, amount);      // ← tokens minted here

        bool valid = _verifyProof(proof, recipient, amount);
        require(valid, "Invalid proof");           // ← reverts BUT mint already happened

        processedProofs[proof] = true;
    }

    function _verifyProof(bytes32 proof, address recipient, uint256 amount)
        internal view returns (bool)
    {
        // Simplified: oracle attests to deposit on source chain
        // In reality this is a Merkle proof or MPC signature
        return proof != bytes32(0); // trivially true for this demo
    }

    function bridgeOut(address from, uint256 amount) external {
        wrappedToken.burn(from, amount);
        // Trigger source-chain release (off-chain in production)
    }
}

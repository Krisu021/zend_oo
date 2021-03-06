import subprocess
import os, os.path, binascii
import random
from subprocess import call

SC_FIELD_SIZE = 96
SC_FIELD_SAFE_SIZE = 94
SC_PROOF_SIZE = 771
SC_VK_SIZE = 1544
COIN = 100000000

def generate_random_field_element_hex():
    return (binascii.b2a_hex(os.urandom(SC_FIELD_SAFE_SIZE)) + "00" * (SC_FIELD_SIZE - SC_FIELD_SAFE_SIZE))

class MCTestUtils(object):

    def __init__(self, datadir, srcdir):
        self.datadir = datadir
        self.srcdir = srcdir

    def generate_params(self, id):
        params_dir = self._get_params_dir(id)
        if os.path.isfile(params_dir + "test_mc_pk") and os.path.isfile(params_dir + "test_mc_vk"):
            return
        args = []
        args.append(os.getenv("ZENDOOMC", os.path.join(self.srcdir, "zendoo/mcTest")))
        args.append("generate")
        args.append(str(params_dir))

        subprocess.check_call(args)

        assert(os.path.isfile(params_dir + "test_mc_pk"))
        return self._get_vk(params_dir + "test_mc_vk")

    def create_test_proof(
        self, id, epoch_number, end_epoch_block_hash, prev_end_epoch_block_hash,
        quality, constant, pks, amounts):

        params_dir = self._get_params_dir(id)
        if not os.path.isfile(params_dir + "test_mc_pk") or not os.path.isfile(params_dir + "test_mc_vk"):
            return
        proof_path = "{}epoch_{}_wcert_proof".format(self._get_proofs_dir(id), epoch_number)
        args = []
        args.append(os.getenv("ZENDOOMC", os.path.join(self.srcdir, "zendoo/mcTest")))
        args.append("create")
        args.append(str(proof_path))
        args.append(str(params_dir))
        args += [str(end_epoch_block_hash), str(prev_end_epoch_block_hash), str(quality), str(constant)]
        for (pk, amount) in zip(pks, amounts):
            args.append(str(pk))
            args.append(str(int(amount * COIN))) #codebase works in satoshi
        subprocess.check_call(args)
        return self._get_proof(proof_path)

    def _get_params_dir(self, id):
        target_dir = "{}/sc_{}_params/".format(self.datadir, id)
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
        return target_dir

    def _get_proofs_dir(self, id):
        target_dir = "{}/sc_{}_proofs/".format(self.datadir, id)
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
        return target_dir

    def _get_proof(self, proof_path):
        assert os.path.isfile(proof_path)
        proof = open(proof_path, "rb").read()
        assert (len(proof) == SC_PROOF_SIZE)
        return binascii.b2a_hex(proof)

    def _get_vk(self, vk_path):
        assert os.path.isfile(vk_path)
        vk = open(vk_path, "rb").read()
        assert (len(vk) == SC_VK_SIZE)
        return binascii.b2a_hex(vk)
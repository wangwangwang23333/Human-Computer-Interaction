<template>
    <div>
        <el-upload 
        action="imgUpload" 
        :limit="1"
        list-type="picture-card" 
        :auto-upload="false"
        :multiple="false" 
        :file-list="fileList"
        :on-success="uploadSuccess"
        :on-change="handleChange"
        accept="image/png, image/jpeg"
        ref="uploadRef"
        :class="fileList.length >=1 ? 'styleB' : 'styleA'"
        >
            <em slot="default" class="el-icon-plus"></em>
            <div slot="file" slot-scope="{file}">
                <img class="el-upload-list__item-thumbnail" :src="file.url" alt="">
                <span class="el-upload-list__item-actions">
                    <span class="el-upload-list__item-preview" @click="handlePictureCardPreview(file)">
                        <em class="el-icon-zoom-in"></em>
                    </span>
                    <span v-if="!disabled" class="el-upload-list__item-delete" @click="handleRemove(file)">
                        <em class="el-icon-delete"></em>
                    </span>
                </span>
            </div>
        </el-upload>
        <el-dialog :visible.sync="dialogVisible">
            <img width="80%" height="80%" :src="dialogImageUrl" alt="">
        </el-dialog>
    </div>
</template>
<script>
    export default {
        data() {
            return {
                dialogImageUrl: '',
                dialogVisible: false,
                disabled: false,
            };
        },
        props:{
            fileList: Array,
        },
        methods: {
            handleRemove() {
                this.fileList.splice(0, 1);
            },
            handlePictureCardPreview(file) {
                this.dialogImageUrl = file.url;
                this.dialogVisible = true;
            },
            uploadSuccess(response) {
                this.$emit('uploadSuccess', response);
            },
            handleChange(file){
                if (this.fileList.length == 1) {
                    return;
                }
                this.fileList.push(file);
            },
            submitUpload(){
                this.$refs.uploadRef.submit();
            },
        }
    }
</script>

<style scoped>

/deep/.styleA .el-upload--picture-card{
    /* width:110px;
    height:110px;
    line-height:110px; */
    
}
/deep/.styleB .el-upload--picture-card{
    display:none;   
}

</style>